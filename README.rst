========
PowerRelay
========

|license| |build-status|

REST API to control GPIO chips


* Free software: MIT license


Features
========

* TODO


API
===

**Show number of relays**
----
  Returns json data about a the number of relays.

* **URL**

  /relays/count

* **Method:**

  `GET`

* **Success Response:**

  * **Code:** 200
    **Content:** `{ count : 42 }`


**Show relay info**
----
  Returns json data about a relay.

* **URL**

  /relays/:id

* **Method:**

  `GET`

* **Success Response:**

  * **Code:** 200
    **Content:** `{ "relay_id" : 0, "status": "1"}`

  * **Code:** 200
    **Content:** `{ "relay_id" : 0, "status": "0"}`

**Show on/off state of relay**
----
  Returns raw text containing the on/off state.

* **URL**

  /relays/:id/state

* **Method:**

  `GET`

* **Success Response:**

  * **Code:** 200
    **Content:** `1`

  * **Code:** 200
    **Content:** `0`

**Change on/off state of relay**
----
  Change the state of a relay, either on or off.

* **URL**

  /relays/:id/state

* **Method:**

  `PUT`

* **Success Response:**

  * **Code:** 200
    **Content:** `{"status": "ok"}`

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT
    :target: https://raw.githubusercontent.com/prevas-dk/labgrid-powerrelay/master/LICENSE

.. |build-status| image:: https://travis-ci.com/prevas-dk/labgrid-powerrelay.svg?branch=master
    :alt: build status
    :target: https://travis-ci.com/prevas-dk/labgrid-powerrelay
