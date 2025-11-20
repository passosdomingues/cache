Advanced Queueing System Simulator - Build System

Build Targets:
  all/release    - Build optimized release version (default)
  debug          - Build with debug symbols and sanitizers
  profile        - Build for profiling
  test           - Build and run test suite

Utility Targets:
  run-sample     - Run sample simulation
  run-batch      - Run batch simulations
  analysis       - Run Python analysis pipeline
  benchmark      - Performance benchmark
  valgrind-check - Memory leak detection
  profile-run    - Generate profiling data

Clean Targets:
  clean          - Remove build artifacts
  distclean      - Remove build artifacts and results
  veryclean      - Remove all generated files

Development:
  format         - Format source code
  lint           - Static code analysis
  coverage       - Generate code coverage report

Info:
  info           - Show build configuration
  help           - Show this help message