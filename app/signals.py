import re
import os
import json
import pandas as pd


class Signals:
    def __init__(self, json_file_path: str):
        self.data = self.load_data(json_file_path)

    @staticmethod
    def load_data(json_file_path: str):
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"File not found: {json_file_path}")
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)

    @staticmethod
    def separate_params(param: str) -> tuple[str, int]:
        pattern = r"([a-zA-Z]+)(\d+)"
        matches = re.match(pattern, param)

        if matches:
            char = matches.group(1).upper()
            index = int(matches.group(2))

            valid_chars = {'X': 1023, 'Y': 1023, 'T': 1023, 'M': 12287, 'V': 14847, 'CV': 255, 'C': 255}
            if char not in valid_chars:
                raise ValueError(f"Invalid parameter character: {char}")

            if not (0 <= index <= valid_chars[char]):
                raise ValueError(f"Invalid index for parameter {char}: {index}")

            if char == 'C':
                return 'CV', index

            return char, index
        else:
            raise ValueError("Invalid parameter format")

    def get_signals_by_param(self, param: str):
        char, index = self.separate_params(param)
        data_for_char = self.data.get(char)

        if data_for_char is None or index >= len(data_for_char):
            raise ValueError(f"No data found for parameter: {char}-{index}")

        return data_for_char[index]

    def get_signals_by_params(self, params: list[str]) -> list[any]:
        all_params = []

        for param in params:
            try:
                signal_data = self.get_signals_by_param(param)
                signal_data['addr'] = signal_data['dec']
                signal_data['waddr'] = signal_data['dec']
                signal_data['broker'], signal_data['topic'] = None, None
                all_params.append(signal_data)
            except ValueError as e:
                raise ValueError(f"Error for parameter {param}: {str(e)}")

        return all_params

    def get_signals_by_file_params(self, data: pd.DataFrame) -> pd.DataFrame:
        variables = data['Переменная']
        all_params = []

        for variable in variables:
            signal_data = self.get_signals_by_param(variable)
            for column in ['тег', 'Описание']:
                if column in data.columns:
                    column_name = 'desc' if column == 'Описание' else 'name'
                    signal_data[column_name] = data.loc[
                        data['Переменная'] == variable, column
                    ].values[0]
            if 'dec' in signal_data:
                signal_data['addr'] = signal_data['dec']
                signal_data['waddr'] = signal_data['dec']
            signal_data['broker'], signal_data['topic'] = None, None
            signal_data.pop('dec', None)
            signal_data.pop('hex', None)
            all_params.append(signal_data)

        params_df = pd.DataFrame(all_params)
        params_df = params_df.where(pd.notnull(params_df), None)

        column_order = [
            'name', 'type', 'group', 'desc', 'addr', 'baddr', 'size', 'format',
            'space', 'waddr', 'wbaddr', 'enbits', 'bitfirst', 'bitlast', 'access',
            'splitaddr', 'pollonce', 'scale', 'bounds', 'minraw', 'maxraw',
            'mineu', 'maxeu', 'resmin', 'resmax', 'limtype', 'limsource',
            'boundstime', 'topic', 'publish', 'subscribe', 'mqtttype', 'mqttformat',
            'broker', 'mqttstring', 'sub', 'pub', 'retain'
        ]

        params_df = params_df.reindex(columns=column_order)

        return params_df
