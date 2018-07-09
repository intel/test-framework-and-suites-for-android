# NOTE: must executed in code repo root
export ACS_EXECUTION_CONFIG_PATH=$PWD/acs_test_suites
cd acs/acs
python ACS.py -c ACS_CI/CAMPAIGN/ACS_NOVAR_LIN_Campaign -b ACS_CI/BENCHCFG/Bench_Config
