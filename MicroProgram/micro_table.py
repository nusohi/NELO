import argparse
import sys
import xlrd
import xlwt

F0 = ['NOP', 'PCoe', 'GRSoe', 'SHoe', 'RYoe', 'ARoe', 'DRoe', 'SPoe']
F1 = ['NOP', 'PCce', 'GRSce', 'IRce', 'RYce', 'RXce', 'DRce', 'SPce']
F2 = ['NOP', 'ADD', 'ADDC', 'SUB', 'SUBB',
      'AND', 'OR', 'NOT', 'XOR', 'INC', 'DEC']
F3 = ['NOP', 'SRce', 'SLce', 'SVce']
F4 = ['NOP', 'PCinc', 'ARce', 'PSWce']
F5 = ['NOP']
F6 = ['NOP', 'SRC']
F7 = ['NOP', 'RD', 'WR', 'PSWoe', 'PSWce2', 'STI', 'CLI', 'INTA']
F = [F0, F1, F2, F3, F4, F5, F6, F7]

F_B = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
F_bit = [3, 3, 4, 2, 2, 2, 1, 3, 3, 9]


# 表格读入
def calculate_orders(path):
    xlrd.Book.encoding = 'utf8'
    workbook = xlrd.open_workbook(path)
    table = workbook.sheet_by_index(0)
    rows_count = table.nrows
    print(f'总行数：{rows_count}')

    output_table = []
    for row in range(1, rows_count):
        address = table.cell(row, 0).value
        order = table.cell(row, 1).value
        print(f'行:{row} 微地址：{address}  微指令：{order}')
        FN, order_texts = ins2order(order)
        output_row = [address, order] + FN + [order_texts]
        output_table.append(output_row)
    return output_table


# 写入表格
def orders_to_table(order_table, book_name):
    workbook = xlwt.Workbook()
    table = workbook.add_sheet('nuso', cell_overwrite_ok=True)
    head = [u'微地址', u'微指令', u'F0', u'F1', 'F2', 'F3',
            'F4', 'F5', 'F6', 'F7', 'F8', 'F9', '微命令']
    # order_table = head + order_table
    for row, orders in enumerate(order_table):
        for col in range(len(orders)):
            # print(f'开始写入 {row+1}行 {col+1}列')
            table.write(row, col, orders[col])
    workbook.save(book_name)


# instruction to order
def ins2order(order):
    if order == '':
        return ['', '', '', '', '', '', '', '', '', ''], ''

    order.replace('.0','')
    DEC = int(order, 16)    # 16 -> 10
    BIN = ZERO(bin(DEC).replace('0b', ''), 32)          # 10 -> 2

    cur_index = 0
    order_texts = ''
    FN = []
    for index, width in enumerate(F_bit):
        cur_order = BIN[cur_index: cur_index + width]
        index_in_group = int(cur_order, 2)
        cur_index = cur_index + width

        if index < 8:
            if(index_in_group >= len(F[index])):
                return ['index', 'error', '', '', '', '', '', '', '', ''], 'error'
            FN.append(index_in_group)
            order_texts += '' if index_in_group == 0 else (
                F[index][index_in_group] + ' ')
        elif index == 8:
            FN.append(index_in_group)
        elif index == 9:
            NA = hex(index_in_group).replace('0x', '')
            NA = ZERO(NA, 3)
            FN.append(NA)

    order_texts = order_texts.strip().replace(' ', ',')
    return FN, order_texts


def ZERO(value, to_length):
    l = len(value)
    if (l < to_length):
        for _ in range(0, to_length-l):
            value = "0" + value
    return value


# ap = argparse.ArgumentParser()
# ap.add_argument("-f", "--from", required=True, help="path to the excel file")
# ap.add_argument("-o", "--output", required=True, help="path to output the result")
# args = vars(ap.parse_args())

if __name__ == '__main__':
    form_url = 'MicroProgram/micro.xlsx'
    to_url = 'MicroProgram/micro_result.csv'

    input_url = input('输入的文件路径：')
    output_url = input('输出的文件名：')

    input_url = 'MicroProgram/micro.xlsx' if input_url == '' else input_url
    output_url = 'MicroProgram/output3.csv' if output_url == '' else output_url

    orders = calculate_orders(input_url)
    orders_to_table(orders, output_url)
