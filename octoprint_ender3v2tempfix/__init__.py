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
    #
    parse_Ender3V2Temp = re.compile(
        '.*TT::(\d+)\.\d+\.(\d+).+\/\/(\d+)\.\d+\.(\d+).*BB::(\d+)\.\d+\.(\d+).+\/\/(\d+)\.\d+\.(\d+)')

    def check_for_temp_report(self, comm_instance, line, *args, **kwargs):
        # Check to see if we received the broken temperature response and if so extract temperature for octoprint
        #		self._logger.debug("Testing: %s" % line)
        if "TT::" not in line:
            return line
        self._logger.debug("Original: %s" % line)
        m = self.parse_Ender3V2Temp.search(line)
        new_line = (" T:%s.%s /%s.%s B:%s.%s /%s.%s" % (
            m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7), m.group(8)))
        self._logger.debug("Modified: %s" % new_line)
        return new_line

    def TempReport(self, comm_instance, parsed_temperatures, *args, **kwargs):
        self._logger.debug("Before: %s" % parsed_temperatures)
        #		self._logger.debug("After: %s" % parsed_temperatures)
        return parsed_temperatures

    def get_update_information(self, *args, **kwargs):
        return dict(
            ender3v2tempfix=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,

                type="github_release",
                current=self._plugin_version,
                user="SimplyPrint",
                repo="OctoPrint-Ender3V2TempFix",

                pip="https://github.com/SimplyPrint/OctoPrint-Ender3V2TempFix/archive/{target_version}.zip"
            )
        )


__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Ender3V2TempFixPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.temperatures.received": __plugin_implementation__.TempReport,
        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.check_for_temp_report,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
