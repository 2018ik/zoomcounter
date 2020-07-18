import matplotlib.pyplot as plt
from main import create_connection, select_all, get_table_name

label = ['a', 'b', 'c', 'd']
x_vertical = [900, 1800, 4000, 4110]
color = ['r', 'y', 'b', 'g']

if __name__ == '__main__':
    conn = create_connection("example.db")
    TABLE_NAME = get_table_name()
    zoomdata = select_all(conn, TABLE_NAME)
    x_time = []
    y_count = []
    for pair in zoomdata:
        x_time.append(pair[0])
        y_count.append(pair[1])

    #remove obvious outliers
    for x in range(1, len(x_time)):
        if abs(y_count[x] - y_count[x-1]) > 100:
            y_count[x] = y_count[x-1]


    plt.figure(dpi=200)
    plt.plot(x_time, y_count)
    for x in range(len(label)):
        plt.axvline(x=x_vertical[x], color=color[x],label=label[x])
    plt.legend()
    plt.show()