TODO
====

- Check that all batchonnections in operators exist before running simulation
- Double-click on batchlocation parent item should open dialog to edit all children at once
	(provided that all children are of the same class)
- Implement actions for when nothing is selected (e.g. append add a batch location or operator)
- Measure bottlenecks: how full the input / output buffers (percentage-wise) are on average
- Measure/store vital parameters in pandas DataFrame, eg:
  - Production volume vs time for each tool
  - Production throughput vs time for each tool
  - Buffer sizes in between all tools vs time
- Implement down-time schedules
- Implement buffers and operator behaviour around buffers
- Implement cassette transfer machines
- Implement up/down for batchlocations?
- Replace container for stores?
