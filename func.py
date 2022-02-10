def str_dataframe_servis(data_frame, param):
    for key in data_frame[f"{param}"]:
        if len(key) > 30:
            data_frame[f"{param}"] = data_frame[f"{param}"].replace(key, key[:25] + '...')

    return data_frame


def str_dataframe_fil(data_frame, param):
    for key in data_frame[f"{param}"]:
        if 'ФОАО "Халык Банк Кыргызстан' in key:
            data_frame[f"{param}"] = data_frame[f"{param}"].replace(key, 'ФОАО "ХБК' + key[27:])
        elif 'Сберегательная касса' in key:
            data_frame[f"{param}"] = data_frame[f"{param}"].replace(key, 'СК' + key[20:])

    return data_frame
