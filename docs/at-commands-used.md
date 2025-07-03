| AT command                          | Final Response                          | Note                     |
| ----------------------------------- | --------------------------------------- | ------------------------ |
| AT                                  | OK                                      | Module functioning?      |
| AT+CIMI=?                           | OK or ERROR                             | sim inserted?            |
| AT+CREG?                            | OK or ERROR or +CME ERROR : <err>       | registered to network?   |
| AT+CSCS=<chset>                     | OK or ERROR                             | set the character set    |
| AT+CSMP=<fo>[,<vp>[,<pid>[,<dcs>]]] | OK or ERROR                             | set text mode parameters |
| AT+CMGS=<da>[,<toda>]               | OK or OK or ERROR or +CMS ERROR : <err> | send sms                 |
