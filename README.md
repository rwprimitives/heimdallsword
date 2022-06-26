HeimdallSword
=============

**HeimdallSword** is a command line tool and a Python module used for sending emails to multiple recipients using one or multiple sender accounts with customizable email templates.

From the command line, emails can be sent by simply providing the necessary files that contain the list of senders, recipients and the content.

As a Python module, **HeimdallSword** provides several modules which allows you send emails given the necessary requirements.

For full documentation, please visit [heimdallsword.readthedocs.io](https://heimdallsword.readthedocs.io)


Installation
============

This section provides several methods for installing **HeimdallSword**.


From the Source
---------------

**HeimdallSword** can be build and deployed directly from the source. It can be obtained as follows:

    $ git clone https://github.com/rwprimitives/heimdallsword.git


Installing from PyPi
--------------------

It is highly recommended that **HeimdallSword** be installed using `pip` to ensure that the latest version is being used.

To install simply run:

    $ pip install heimdallsword


Getting Started
===============

This section walks you through the different ways **HeimdallSword** can be used as a command line tool.


Basic Usage
-----------

In order to use **HeimdallSword**, a list of senders, recipients and the content to send must be provided. The required information needed is a file that contains the list of sender emails, a file that contains the list of recipients and the directory path containing the content to be sent to the recipients.

**HeimdallSword** has offers two methods in which the required information can be provided.

The first method is the `individual arguments` set. It provides the individual flags to set file paths and directory paths required. The `-s` flag is used to specify the file that contains the list of senders. The `-r` flag is used to specify the file that contains the list of recipients. The `-c` flag is used to specify the directory path that contains the files with the content to be sent to each recipient. For example:

    $ heimdallsword -s senders.txt -r recipients.txt -c /path/to/content

The second method is the `combined arguments` set. It provides a single flag to set the directory path where all of the required content is located. In order to use the `-p` flag, pre-defined file and directory names must be used. For the sender emails the file must be named `senders.txt`. For the recipient emails the file must be named `recipients.txt`. The content directory must be named `content` which should contains the files with the content to be sent to each recipient. For example:

    $ heimdallsword -p /path/to/all/messages/

The directory `messages` should have all of the required files and directories as such:

    $ tree /path/to/all/messages/

    messages
    ├── senders.txt
    ├── recipients.txt
    └── content
        ├── msg1.txt
        ├── msg2.txt
        └── msg3.txt


Synopsis
--------

To view the different options supported, execute `heimdallsword` with `-h` or `--help` option:

    usage: heimdallsword [-h] [-d] [-g] [-lf] [-m] [-mf] [-w] [-v] [-c] [-r] [-s] [-p] [-t]

    A tool for sending emails to multiple recipients using one or multiple sender accounts with customizable email templates.

    optional arguments:
      -h, --help                show this help message and exit
      -d, --delay               the time in milliseconds between each email sent (default: 100 ms)
      -g, --enable-graphics     enables command line graphical interface
      -lf, --log-file           the log file used to store data (default: ./heimdallsword.log)
      -m, --metrics-delay       the time in seconds to wait after the last email sent before gathering metrics (default: 120 secs)
      -mf, --metrics-file       the metrics file used to store data (default: ./metrics.txt)
      -w, --worker-count        the number of worker threads to use for sending emails (default: 80)
      -v, --version             show program's version number and exit

    individual arguments:
      -c, --content-dir         the directory path to the email body templates (i.e., content)
      -r, --recipients          the recipients file (i.e., recipients.txt)
      -s, --senders             the senders file (i.e., senders.txt)

    combined arguments:
      -p, --process-all         the directory path which contains the recipients.txt, senders.txt and content directory

    testing arguments:
      -t, --test-sender-login   the sender file to test login authentication (i.e., senders.txt)


Sender File
-----------

The `sender file` must contain one or multiple emails that will serve as the sender to each recipient. Each line represents a sender and must be in the following format:

    sender_email, password, smtp_url=smtp.domain.com, smtp_port=587, pop3_url=pop.domain.com, pop3_port=995

The `smtp_url` and `smtp_port` key-value pairs are optional. If the SMTP server requires a subdomain (i,e,: smtp.domain.com), then `smtp_url` must be defined. By default, `smtp_url` is set to the domain of the sender's email. If the SMTP server port is not the default 587 SMTP port, then use `smtp_port` to specify the custom SMTP port number. Same concept applies to `pop3_url` and `pop3_port` in order to read emails using POP3 protocol. The default port used for POP3 is 995.

Below is an example of commonly known email services and a private email server:

    eldiablomerc@gmail.com, ElD!@bl0P@$$, smtp_url=smtp.gmail.com, pop3_url=pop.gmail.com
    eldiabloevil@outlook.com, Ev!lD33d$, smtp_url=smtp-mail.outlook.com, pop3_url=pop-mail.outlook.com
    eldiablokills@yahoo.com, D3adFAc3, smtp_url=smtp.mail.yahoo.com, pop3_url=pop.mail.yahoo.com
    eldiablodoes@myownemailserver.com, Secretz

It is highly recommended to use **App Passwords** for all sender emails if possible. Some email provides like gmail and yahoo will only allow the use of **App Passwords** to authenticate.

To skip a specific sender, simply add a `#` symbol at the beginning of the line and it will be ignored.


Recipient File
--------------

The `recipient file` can contain one or multiple email recipients. Each line represents a recipient and must be in the following format:

    recipient_email, content_file

The `content file` is the name of the file which contains the information needed to construct an email, for example: subject, content type and body. For more details, see the [Content File](content-file).

**HeimdallSword** support customizable email templates. This makes the process simple for sending the same email to multiple recipients using a single template at a large escale. The way customizale email templates works is by using key-value pairs. The key must be wrapped inside a `${}` (i,e,: ${key}) and reside in the body section of the content file. The key-value pairs must be defined for each recipient in the recipients file and must be comma separated after the `content_file` is defined. **HeimdallSword** will read each recipient, parse the key-value pairs and read the content file to search for the keys and insert the value in the message body. This is done for each recipient as seen in the following example:

    client1@gmail.com, messageA.txt, GREETING=Morning, ID=123ABC, COMPANY=ABC Business
    client2@outlook.com, messageA.txt, GREETING=Afternoon, ID=987ZXY, COMPANY= livE Corp
    client2@nokeys.com, nokeysmessage.txt

The body of the message would include the keys as such:

    ${GREETING},

    Thank you for submitting your request. Your random generated identification number is ${ID}.

    Sincerely,
    ${COMPANY}

Additionally, **HeimdallSword** provides a set of built-in keys that can be used in any template without specifying any values. The following example shows how these built-in keys are used in the body of a message:

    Recipient Email:            ${EMAIL}
    Recipient Email Username:   ${EMAIL_USERNAME}
    Recipient Email Domain:     ${EMAIL_DOMAIN}
    Local Date (Default):       ${LOCAL_DATE}
    Local Date yyyy-mm-dd:      ${LOCAL_DATE=%Y-%m-%d}
    Local Time (Default):       ${LOCAL_TIME}
    Local Time hh:mm:ss am/pm:  ${LOCAL_TIME=%H:%M:%S %p}
    Local Date and Time:        ${LOCAL_DATE=%a %d %b %Y %H:%M:%S %p %Z}

    UTC Date (Default):         ${UTC_DATE}
    UTC Date yyyy-mm-dd:        ${UTC_DATE=%Y-%m-%d}
    UTC Time (Default):         ${UTC_TIME}
    UTC Time hh:mm:ss am/pm:    ${UTC_TIME=%H:%M:%S %p}
    UTC Date and Time:          ${UTC_DATE=%a %d %b %Y %H:%M:%S %p %Z}

When the LOCAL_DATE and LOCAL_TIME keys are used in an email template, **HeimdallSword** will insert the current date and time of the host system; same applies for UTC_DATE and UTC_TIME with the only exception that it uses UTC time instead of the default timezone on the host system. Furthermore, format values can be specified to the date and time keys followed by an equals symbol as seen in the examples above. The format argument are the format codes that the 1989 C standard requires. For more details on the type of formatting directives available, go to [https://docs.python.org/3/library/time.html#time.strftime](https://docs.python.org/3/library/time.html#time.strftime).

To skip a specific recipient, simply add a `#` symbol at the beginning of the line and it will be ignored.

Content File
------------

The `content file` is an email template that contains the information needed to construct an email. As mentioned in the [Recipient File](recipient-file) section, built-in and custom keys can be added within the body section to help tailor the email to each recipient. Each `content file` must be saved within a designated `content` directory along with the rest of the content files. A `content file` must have a line that defines the subject line, the content type of email template (i.e., plain or html) and the body. These lines must be defined in the following order:

    suject=
    content_type=
    body=

The `content_type` should have either `plain` for regular text or `html` if the body contains HTML tags and CSS styling. Note that JavaScript is not supported in emails. The following example is a plain email template using built-in keys as well as user-defined key-value pairs:

    suject=Registration Complete
    content_type=plain
    body=
    Welcome ${EMAIL_USERNAME},

    Thank you for registering. We are glad to have you join our team. Please save the following code as you will need this to authenticate: ${CODE}

    This email was automatically generated on ${LOCAL_DATE} at ${LOCAL_TIME}.

    Best wishes,
    ${COMPANY}

The body line must be the last line defined as **HeimdallSword** parser will treat anything after `body=` as part of the body. The content must follow the UTF-8 character set standard.

Any `content files` that contain HTML must incorporate all styling. Any media sources that is part of the HTML email must be hosted on an active web server and the URLs for the sources must be embedded in the HTML content of the message. The following example is an HTML email template using built-in keys as well as user-defined key-value pairs with CSS styling and embedded URL:

    subject=Registration Complete
    content_type=html
    body=
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8" />
        <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style type="text/css">
        body {
            background-color: #f0f0f2;
            margin: 0;
            padding: 0;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
        }
        div {
            width: 600px;
            margin: 5em auto;
            padding: 2em;
            background-color: #fdfdff;
            border-radius: 0.5em;
            box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);
        }
        a:link, a:visited {
            color: #38488f;
            text-decoration: none;
        }
        @media (max-width: 700px) {
            div {
                margin: 0 auto;
                width: auto;
            }
        }
        </style>    
    </head>
    <body>
    <div>
        <h1>${GREETING} ${EMAIL_USERNAME},</h1>
        <p>Thank you for using HeimdallSword. We are glad that you are using this amazing tool. Please save the following random code for no reason: ${CODE}</p>
        <p>Don't forget to visit this link <a href="https://heimdallsword.readthedocs.io/en/latest/">for more information...</a></p>
        <p>Best wishes,</br>${AUTHOR}</p>
        </br>
        <p>This email was automatically generated on ${LOCAL_DATE} ${LOCAL_TIME}.</p>
    </div>
    </body>
    </html>


Metrics
-------

**HeimdallSword** provides a metrics summary of all emails sent to help determine the success rate. Once all of the emails are sent, metrics are stored in a file called `metrics.txt` by default. However, a custom name can be provided by using the `-mf` or `--metrics-file` flags. When a sender sends an email to a recipient and the email bounced, the sender typically receives a reply within two minutes. In order to determine if emails have bounced, **HeimdallSword** has to wait two minutes by default after an email is sent and reading the sender inbox to determine if the email bounced or not. The two minute delay can be configured by using the `-m` or `--metrics-delay` flags. Below is an example of the content stored in the metrics file:

    Total senders = 3
    Total recipients = 7
    Start time = 05/29/2022 15:33:07.529535
    Stop time = 05/29/2022 15:33:14.558725
    Delivery rate = 100.0%
    Fail rate = 0.0%
    Emails delivered = 7
    Emails not delivered = 0
    Emails failed delivery = 0
    Recipients rejected = 0
    Senders rejected = 0
    Emails failed delivery format = 0
    Emails failed deivery disconnect = 0


Logging
-------

**HeimdallSword** prints logging information on the terminal and at the same time it saves the logs into a file named `heimdallsword.log`. Every time **HeimdallSword** runs, it opens the file `heimdallsword.log` and appends any logging information it generates. The name of the log file can be changed by using the `-lf` or `--log-file` flags. The logs **HeimdallSword** generate helps determine the current state of the email sending process, it provides information about failed attempts with reasons why it failed to send an email and metrics. 


Graphical Interface
-------------------

**HeimdallSword** produces a beautifully designed command line graphical interface which provides live metrics update as emails are sent as well as logging information. To enable the command line graphical interface, specify the `-g` or `--enable-graphics` flags. 


Recipient List Sanitization
---------------------------

As **HeimdallSword** attempts to send emails from a given list of recipients, recipients that are considered bad due to bounced emails or recipient no longer exists are saved in a file called `bad_recipients.txt`. Same concept is applied for good recipients and are stored in a file called `good_recipients.txt`.
