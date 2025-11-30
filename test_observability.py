from observability import ObservabilityManager

obs = ObservabilityManager()
report = obs.get_performance_report()

print("Performance Report:", report)
