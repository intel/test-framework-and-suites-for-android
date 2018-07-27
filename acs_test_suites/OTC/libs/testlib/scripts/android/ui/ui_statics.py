#!/usr/bin/env python
"""
Copyright (C) 2018 Intel Corporation
?
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
?
http://www.apache.org/licenses/LICENSE-2.0
?
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.
?

SPDX-License-Identifier: Apache-2.0
"""


watcher_list = {'mock_watcher': {'groups': ['mock'],
                                 'selector': {'textContains': 'Process system isn\'t responding.'},
                                 'action': 'click',
                                 'action_view': {'text': 'OK'},
                                 },
                'process_system': {'groups': ['wifi', 'cts'],
                                   'selector': {'textContains': 'Process system isn\'t responding.'},
                                   'action': 'click',
                                   'action_view': {'text': 'OK'},
                                   },
                'quick_settings': {'groups': ['wifi', 'cts'],
                                   'selector': {'resourceId': 'com.android.systemui:id/quick_settings_container'},
                                   'action': 'press',
                                   'action_view': 'back',
                                   },
                'app_has_stopped': {'groups': ['wifi', 'cts'],
                                    'selector': {'textContains': 'has stopped.'},
                                    'action': 'click',
                                    'action_view': {'text': 'OK'},
                                    },
                'M_SD_Card': {'groups': ['wifi', 'cts'],
                              'selector': {'textContains': 'This SD Card'},
                              'action': 'click',
                              'action_view': {'text': 'Ok'},
                              },
                'startup_wizard_SIM': {'groups': ['wifi', 'cts'],
                                       'selector': {'textContains': 'Select SIM card'},
                                       'action': 'press',
                                       'action_view': 'back',
                                       },
                'p2p_invitation': {'groups': ['wifi'],
                                   'selector': {'text': 'Invitation to connect'},
                                   'action': 'click',
                                   'action_view': {'text': 'Decline'},
                                   }
                }


handler_list = {'mock_watcher': {'groups': ['mock'],
                                 'selector': {'textContains': 'Process system isn\'t responding.'},
                                 'action': 'click',
                                 'action_view': {'text': 'OK'},
                                 },
                'process_system': {'groups': ['wifi', 'cts'],
                                   'selector': {'resourceId': 'android:id/button2', 'text': 'Wait'},
                                   'action': 'click',
                                   'action_view': {'text': 'OK'},
                                   },
                'quick_settings': {'groups': ['wifi', 'cts', 'aft'],
                                   'selector': {'resourceId': 'com.android.systemui:id/quick_settings_container'},
                                   'action': 'press',
                                   'action_view': 'back',
                                   },
                'app_has_stopped': {'groups': ['wifi', 'cts', 'aft'],
                                    'selector': {'textContains': 'has stopped.'},
                                    'action': 'click',
                                    'action_view': {'text': 'OK'},
                                    },
                'M_SD_Card': {'groups': ['wifi', 'cts', 'aft'],
                              'selector': {'textContains': 'This SD Card'},
                              'action': 'click',
                              'action_view': {'text': 'Ok'},
                              },
                'startup_wizard_SIM': {'groups': ['wifi', 'cts', 'aft'],
                                       'selector': {'textContains': 'Select SIM card'},
                                       'action': 'press',
                                       'action_view': 'back',
                                       },
                'p2p_invitation': {'groups': ['wifi'],
                                   'selector': {'text': 'Invitation to connect'},
                                   'action': 'click',
                                   'action_view': {'text': 'Decline'},
                                   },
                'google_check': {'groups': ['wifi', 'cts'],
                                 'selector': {'textContains': 'Allow Google to regularly check device activity'},
                                 'action': 'click',
                                 'action_view': {'resourceId': 'com.android.vending:id/positive_button'},
                                 # 'action_view': {'text':'ACCEPT'},
                                 },
                'select_sim_data': {'groups': ['wifi', 'cts'],
                                    'selector': {'textContains': 'Select a SIM for data'},
                                    'action': 'click',
                                    'action_view': {'resourceId': 'com.android.settings:id/title', 'index': 0},
                                    },
                'modem_unrecoverable': {'groups': ['wifi'],
                                        'selector': {'textContains': 'modem unrecoverable'},
                                        'action': 'click',
                                        'action_view': {'text': 'OK'},
                                        },
                'goole_app_stopped': {'groups': ['wifi'],
                                      'selector': {'textContains': 'Google App has stopped'},
                                      'action': 'click',
                                      'action_view': {'text': 'Close'},
                                      }
                }
