import sys
import re
import subprocess
import pprint
import glob


class DinoLiteUVCControl:
    def __init__(self, args):
        self.args = args
        if self.args.debug:
            self.pp = pprint.PrettyPrinter(indent=4)
        device_re = re.compile(r"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        df = subprocess.check_output("lsusb", universal_newlines=True)
        devices = []
        for i in df.split('\n'):
            if i:
                info = device_re.match(i)
                if info:
                    print(i)
                    dinfo = info.groupdict()
                    dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                    devices.append(dinfo)
        self.ourDevices = []
        for device in devices:
            if "a168" in device['id']:
                idlist = device['id'].split(":")
                print(idlist)
                if "0980" in idlist[1]:
                    self.log("Found AnMo device 0980")
                    # initialize 0980, 5mp shiny microscope
                    from .devices import device0980
                    tmpObj = device0980.Device0980(self)
                    self.ourDevices.append(tmpObj)
                if "0970" in idlist[1]:
                    self.log("Found AnMo device 0970")
                    # initialize 0970, 2mp shiny microscope
                    from .devices import device0970
                    tmpObj = device0970.Device0970(self)
                    self.ourDevices.append(tmpObj)
                if "0890" in idlist[1]:
                    self.log("Found AnMo device 0890")
                    # initialize 0890, 1.xMP flat color microscope
                    # This one needs the kernel patch for LED control to work, and no FLC control
                    from .devices import device0890
                    tmpObj = device0890.Device0890(self)
                    self.ourDevices.append(tmpObj)
        self.log("Devices:")
        self.log(self.ourDevices)
        if len(self.ourDevices) > 1:
            vids = glob.glob("/dev/video*")
            for device in self.ourDevices:
                for vid in vids:
                    addy = subprocess.check_output(["udevadm", "info", "-q", "path", "-n", vid])
                    large_out = subprocess.check_output(["udevadm", "info", "-a", "-p", addy.rstrip()])
                    outList = large_out.split("\n")
                    id_list = []
                    for line in outList:
                        if "idProduct" in line:
                            id_list.append(line.split('"')[1])
                    for productId in id_list:
                        if device.product_id in productId:
                            device._set_vid_address(vid)
            self.log(self.ourDevices[0].vid_address)
            self.log(self.ourDevices[1].vid_address)

    def log(self, data):
        if self.args.debug:
            self.pp.pprint(data)

    def work(self):
        pass

    def cleanup(self):
        pass

    def display_shutdown_message(self, returncode):
        print("Exited with %s exitcode!" % str(returncode))
        sys.exit(int(returncode))
