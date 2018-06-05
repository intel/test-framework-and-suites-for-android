import time
import traceback

from acs.Core.Report.Live.ReportUtils.ReportLogging import LOGGER_REPORT
from acs.Core.Report.Live.ReportUtils.ReportLogging import push_metrics
from acs.Core.Report.Live.ReportUtils.utils import StatusCode
from acs.UtilitiesFWK.Utilities import get_class
from acs.UtilitiesFWK.Patterns import Singleton

from Queue import Queue
from threading import Thread
from threading import Timer

ADAPTER_CLASS_MAP = 'acs.Core.Report.Live.ReportUtils.adapters.{module_name}.{class_name}Adapter'
ERROR_CODE_TO_RETRY = [StatusCode.CONNECTION_ERROR,
                       StatusCode.TIMEOUT,
                       StatusCode.HTTP_CODE_ERROR.format(status_code=404),
                       StatusCode.HTTP_CODE_ERROR.format(status_code=503)]
RETRY_TIMEOUT = 600


@Singleton
class AdapterManager(object):

    """
    Protocol Manager aims at using the protocol to use to send requests to the report server
    """
    _protocol_instance = None
    _queue = None
    _run_retry = True
    _retrying_thread = None
    _timer = None

    def __init__(self):
        self._queue = Queue()
        self._run_retry = True
        self._timer = Timer(RETRY_TIMEOUT, self._stop_retrying)
        self._retry_thread = Thread(target=self._retry_send_requests)
        self._retry_thread.name = "ReportingServiceThread"
        self._retry_thread.start()

    def init(self, report_server_adapter='tcr', **kwargs):
        report_server_adapter = report_server_adapter.upper()
        self._protocol_instance = get_class(ADAPTER_CLASS_MAP.format(module_name=report_server_adapter,
                                                                     class_name=report_server_adapter))(**kwargs)

    @property
    def campaign_url(self):
        """
        Return user link to report server
        :return: report server url
        """
        return self._protocol_instance.campaign_url

    def send_new_request(self, action, data):
        """
        This method is called to register a new request to send to the report server

        :param action: action to execute
        :type action: str

        :param data: data to send
        :type data: dict
        """
        # Initialize data dictionary
        data.setdefault('header', {'requestId': -1})
        data.setdefault('payload', {})

        # Extract header and payload from data
        header_req_id = data['header']['requestId']
        payload = data['payload']

        # Initialize data for metrics server
        data_metrics = {'event': action, 'eventId': header_req_id}

        if header_req_id == -1:
            error_msg = "No 'requestId' defined in the header of data '{}'".format(data)
            LOGGER_REPORT.error("action: {} - error: {}".format(action, error_msg))
            data_metrics.update({'errorCode': StatusCode.WRONG_DATA_FORMAT, 'errorMessage': error_msg})

        elif not isinstance(payload, dict) and not isinstance(payload, list):
            error_msg = "'payload' shall be a dictionary or a list'{}'".format(data)
            LOGGER_REPORT.error("action: {} - error: {}".format(action, error_msg))
            data_metrics.update({'errorCode': StatusCode.WRONG_DATA_FORMAT, 'errorMessage': error_msg})
        elif not payload:
            error_msg = "'payload' is empty, no data will be sent to the report server"
            LOGGER_REPORT.warning("action: {} - error: {}".format(action, error_msg))
            data_metrics.update({'errorCode': StatusCode.EMPTY_DATA, 'errorMessage': error_msg})
        else:
            # Start the last chance timer on a specific event
            if action == "send_campaign_resource":
                self._timer.start()

            # Put the data into the queue
            self._queue.put((action, data))

            # Push data to metrics server
            data_metrics.update({'requestAskTime': time.time()})

        if 'errorCode' in data_metrics:
            data_metrics['receivedData'] = repr(data)
            data_metrics['callStack'] = repr(traceback.format_stack())

        # Push data to metrics server
        push_metrics(**data_metrics)

    def _send_request(self, action, data):
        """
        This method is called to send request to the report server

        :param action: action to execute
        :type action: str

        :param data: data to send
        :type data: dict

        :return: report server response
        :rtype: json/object
        """
        action_method = getattr(self._protocol_instance, action)
        response = action_method(data.get("header"), data.get("payload"))
        return response

    def _retry_send_requests(self):
        """
        Handler to retry sending request
        """
        request = None
        retry = 0

        while self._run_retry:
            if not request and not self._queue.empty():
                request = self._queue.get()

            if request:
                start_time = time.time()
                # Send the request to the server and wait for response
                # TODO: response.elapsed (requests.models.Response) may do the trick for you
                response = self._send_request(*request)
                stop_time = time.time()

                # Get error code/message if any
                error_code = response.get("errorCode", StatusCode.NO_ERROR) if response else StatusCode.NO_RESPONSE
                error_msg = response.get("errorMessage", "No error") if response else "No response"

                # Push data to metrics server
                push_metrics(event=request[0],
                             eventId=request[1]["header"]["requestId"],
                             requestStartTime=start_time,
                             requestStopTime=stop_time,
                             errorCode=error_code,
                             errorMessage=error_msg)

                if response and error_code not in ERROR_CODE_TO_RETRY:
                    # Stop the timer when receiving 'send_campaign_resource' event
                    if request[0] == "send_campaign_resource":
                        if self._timer:
                            self._timer.cancel()
                        self._run_retry = False
                    request = None
                    retry = 0
                else:
                    retry += 1

            # Increase the timeout to avoid polluting the server
            time.sleep(0.5 * retry)

    def _stop_retrying(self):
        """
        Handler to stop retrying when global timeout is reached
        """
        self._run_retry = False
        LOGGER_REPORT.warning("Global Timeout {}s has been reached ! "
                              "Stopping retry mechanism ! All pending requests will be lost".format(RETRY_TIMEOUT))

    def get_protocol(self):
        return self._protocol_instance
