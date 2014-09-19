TODO
====

- Implement idle time presentation dialog / change batch locations accordingly
- Start counting idle time on receiving first batch of wafers
- Add button that starts simulation of selected tool at maximum throughput
- Implement down-time schedules
- Implement cassette transfer machines
- Implement buffers and operator behaviour around buffers
- Implement batchtex with variable texture baths
- Implement batchchem
- Implement ion implant
- Measure bottlenecks: how full the input / output buffers (percentage-wise) are on average
- Measure/store vital parameters in pandas DataFrame, eg:
  - Production volume vs time for each tool
  - Production throughput vs time for each tool
  - Buffer sizes in between all tools vs time
- Implement up/down for batchlocations?
- Replace container for stores?
