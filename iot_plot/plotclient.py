#!/usr/bin/env python3

from json import dumps

class MQTTPlotter:

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    # create a new series on remote
    # all data of a prior series with the same name will be lost
    # arguments:
    #    series name (first)
    #    column names
    def new_series(self, *args):
        self.mqtt_client.publish("new_series", dumps(args))

    # add data to series on remote, use after 'new_series'
    # arguments:
    #    series name
    #    column values (same number as column names submitted wiht new_series)
    def data(self, *args):
        self.mqtt_client.publish("data", dumps(args))

    # store series on remote in pickle format
    def save_series(self, series, filename=None):
        self.mqtt_client.publish("save_series", dumps([ series, filename ]))

    # plot series on remote
    def plot_series(self, series, **kwargs):
        self.mqtt_client.publish("plot_series", dumps([ series, kwargs ]))

    # evaluate python code on remote
    # Beware: security hole!
    # enable in plot_server if desired
    def exec_remote(self, code):
        print("------------ exec_remote:", code)
        self.mqtt_client.publish("exec_remote", dumps(code))


def sample_plot():
    from mqttclient import MQTTClient
    from math import sin, cos, exp, pi

    mqtt = MQTTClient("iot.eclipse.org")
    mp = MQTTPlotter(mqtt)

    # give the series a unique name (in case you create multiple plots)
    SERIES = "sinusoid"

    # data column names
    mp.new_series(SERIES, 'time', 'cos', 'sin', 'sin*cos')

    # generate the data
    def f1(t): return cos(2 * pi * t) * exp(-t)
    def f2(t): return sin(2 * pi * t) * exp(-t)
    def f3(t): return sin(2 * pi * t) * cos(2 * pi * t) * exp(-t)
    for t in range(200):
        t *= 0.025
        # submit each datapoint to the plot server
        mp.data(SERIES, t, f1(t), f2(t), f3(t))

    # save data as pkl document
    # see plot_load_pkl.py for an example of loading it back into python
    mp.save_series(SERIES)

    # create a plot, default dir is $IoT49
    mp.plot_series(SERIES,
        filename="example.pdf",
        xlabel="Time [s]",
        ylabel="Voltage [mV]",
        title=r"Damped exponential decay $e^{-t} \cos(2\pi t)$")

    # wait until all data is transferred or no plot will be generated ...
    import time
    time.sleep(5)


if __name__ == "__main__":
    try:
        sample_plot()
    except KeyboardInterrupt:
        pass