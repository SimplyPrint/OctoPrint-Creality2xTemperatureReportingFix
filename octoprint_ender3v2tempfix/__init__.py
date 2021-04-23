# coding=utf-8
# All code, with the only exception being formalities and formatting, is made by community member b-morgan,
#  because of the issue discussed in this thread;
#  https://community.octoprint.org/t/temperature-reporting-now-working-with-new-ender-3-v2/21053
# Distributed with his accept, due to testing limitations

from __future__ import absolute_import, unicode_literals
import octoprint.plugin
import re


class Ender3V2TempFixPlugin(octoprint.plugin.OctoPrintPlugin):
    #
    # Recv:   TT::27.7627.76  //0.000.00  BB::39.3539.35  //0.000.00  @@::00  BB@@::00
    # Recv:  T:23.84 /0.00 B:24.05 /0.00 @:0 B@:0

    double_pattern = '(-?\d+)\.\d+-?\d+\.(\d+)\s*//\s*(\d+)\.\d+\d+\.(\d+)'
    parse_hotend_temp = re.compile('(T\d*)\\1::' + double_pattern)
    parse_bed_temp = re.compile('(B)\\1::' + double_pattern)
    parse_chamber_temp = re.compile('(C)\\1::' + double_pattern)
    fix_template = "{heater}:{current1}.{current2} /{actual1}.{actual2}"

    def check_for_temp_report(self, comm_instance, line, *args, **kwargs):
        # Check to see if we received the broken temperature response and if so extract temperature for octoprint
        if "TT::" not in line and "BB::" not in line and "CC::" not in line:
            return line
        self._logger.debug("Original: {}".format(line))

        for pattern in (self.parse_hotend_temp, self.parse_bed_temp, self.parse_chamber_temp):
            for m in pattern.finditer(line):
                line = line.replace(m.group(0), self.fix_template.format(heater=m.group(1),
                                                                         current1=m.group(2),
                                                                         current2=m.group(3),
                                                                         actual1=m.group(4),
                                                                         actual2=m.group(5)))

        self._logger.debug("Modified: {}".format(line))
        return line

    def get_update_information(self, *args, **kwargs):
        return dict(
            ender3v2tempfix=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,

                type="github_release",
                current=self._plugin_version,
                user="SimplyPrint",
                repo="OctoPrint-Creality2xTemperatureReportingFix",

                pip="https://github.com/SimplyPrint/OctoPrint-Creality2xTemperatureReportingFix/archive/{target_version}.zip"
            )
        )


__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Ender3V2TempFixPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.received": (__plugin_implementation__.check_for_temp_report, 1),
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
