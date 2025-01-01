# AT Commands

| Scenario                   | Command  | Description                           | Response                                 | Note |
| -------------------------- | -------- | ------------------------------------- | ---------------------------------------- | ---- |
| module powered off         | AT       | check if the module is functioning    | user command and response both are empty |      |
| module powered without sim | AT       | check if the module is functioning    | OK                                       |      |
| module powered without sim | AT+CIMI  | check if sim is inserted              | +CME ERROR: SIM not inserted             |      |
| module powered with sim    | AT+CIMI  | check if sim is inserted              | <some long number>                       |      |
|                            | AT+CSPN? | get the service provider from the sim | +CSPN: <spn>,<display mode>              |      |
|                            | AT+CREG? | To get network registration status    | +CREG:<n>,<stat>                         |      |
|                            | AT+CSQ   | get the signal strength               | +CSQ:<rssi>,<ber>                        |      |
|                            | AT+CSCA? | gives the phone number?               |                                          |      |
