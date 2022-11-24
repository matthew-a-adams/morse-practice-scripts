from qrz import QRZ

import morse


def print_keys(key_names, query_result):
    """
    Prints results and does not throw exception on queries
    like W1AW where fname key does not exist
    """
    info = ""
    for key_name in key_names:
        if key_name in query_result:
            info += query_result[key_name] + " "
    print(info)


if __name__ == '__main__':
    qrz = QRZ('./settings.cfg')
    result = qrz.randomOperator()
    print(result['call'])
    #print_keys(['call'],result)
    #print_keys(['fname'], result)
    #print_keys(['addr2', 'state'], result)

    sounder = morse.audio()
    sounder.play(result['call'])