## Test Campaign Definition

A Test Campaign is an XML file that describes a sequence of test scenarios.

It defines the list of test cases to be executed, and customize the execution flow (expected DUT state at the end of the execution, stop/continue execution after a failure, etc.)


### Test Campaign anatomy
A campaign is structured in 3 blocks:

```xml
<Campaign>
    <Parameters>
    ** This node contains Parameter nodes, describing campaign execution flow behavior **
    </Parameters>

    <Targets>
     ** This node contains Target nodes, used to set campaign target pass rate **
    </Targets>

    <TestCases>
    ** This node contains TestCase nodes, describing campaign test plan **
    </TestCases>
</Campaign>
```

#### Parameters
Parameters section is used to define:

* if equipment has to be used to control DUT
* if reboot can be done according to specific test case verdict
* if campaign execution has to be stopped according to specific test case verdict
* logging level
* DUT state at the end of campaign execution

Here is the list of possible parameters:

Parameters| Description | Example
------------| ----------------|----------------
**skipBootOnPowerCycle**| if set to *True*, ACS boot procedure will be disabled. It means that boot will be handle inside the campaign/TC | `<Parameter skipBootOnPowerCycle="True" />`
**bootRetryNumber**| This parameter defines the maximum number of boot retries before declaring a DUT boot as failed. | `<Parameter bootRetryNumber="0" />`
**powerCycleOnFailure**| if set to *True*, A reboot of DUT will be done each time a test case is failed | `<Parameter powerCycleOnFailure="False" />`
**stopCampaignOnCriticalFailure**| if set to *True*, any test case declared as **CRITICAL** will interrupt the campaign execution; When such error occurs, campaign result is declared as **failed** because next test cases will be **not executed**; When such error occurs at the end of the campaign execution and all test are **pass**, campaign is declared as **successful**. | `<Parameter stopCampaignOnCriticalFailure="True" />`
**stopCampaignOnFirstFailure**|  if set to *True*, the first test case failure will stop the campaign execution | `<Parameter stopCampaignOnFirstFailure="False" />`
**finalDutState**| This parameter defines the final DUT state at the end of the campaign | `<Parameter finalDutState="NoChange" />`
**loggingLevel**| This parameter defines the ACS logger level.|`<Parameter loggingLevel="info" />`

#### Targets
Targets section is used to define specific test case pass rate.
```xml
<Target targetB2bPassRate="90"/>
```
This defines a back to back iteration target (as a %). All test cases that have a **b2bIteration** > 1 will have to reach this target in order to be passed. Thus a test with b2bIteration = 100 will have to succeed at least 90 times to be declared **passed**, else it will be considered **failed**.

#### TestCases

TestCases section defines which test cases will be run by this campaign.
It contains ``<TestCase>`` nodes, each node pointing to a test case XML file.

```xml
<TestCases>
	<TestCase Id="./myTestCase1"/>
	<TestCase Id="./myTestCase2"/>
	<TestCase Id="./aTestCaseFolder/myTestCase3"/>
</TestCases>
```
This campaign will run **myTestCase1**, **myTestCase2** then **myTestCase3** test cases.

**Note**:
**Id** attribute value can be either:

* a relative path between campaign and the test case **without '.xml' extension**
* a relative path between *_ExecutionConfig* folder and the test case **without '.xml' extension**



