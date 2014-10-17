TODO
====

- Implement down-time settings for whole tools (SSE in particular)
- Implement down-time settings for tube furnace and PECVD
- Implement ion implant
- Add calculation of nominal speed and generate utilization rate
- Try to speed up inline tools like PrintLine
  - Have a single data structure that represents all possible unit positions
  - Have one process that updates positions in time
- Measure/store vital parameters in pandas DataFrame, eg:
  - Production volume vs time for each tool
  - Production throughput vs time for each tool
  - Buffer sizes in between all tools vs time
- Add load/save feature for individual tools?
