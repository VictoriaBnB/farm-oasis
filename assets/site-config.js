/* victoriabnb.ca — site settings.
   Easiest way to change anything here: double-click "Site Manager.pyw" in this folder,
   edit, then press "Publish to website". (Or edit this file by hand and push.)

   properties.<name>.status:  "open"   = bookable (normal)
                              "paused" = shown, but marked "not taking bookings right now"
                              "hidden" = removed from the home page, booking form and calendar
   pricing.<name>.seasons:    nightly rate by date range (MM-DD, inclusive; may wrap the year end)
   pricing.<name>.discounts:  % off the nightly subtotal for stays of at least minNights
   pricing.<name>.monthly:    fixed price for perNights nights, applied to stays of minNights or more
   analytics:                 leave blank for none; GoatCounter code (e.g. "victoriabnb") or GA4 id ("G-XXXXXXX")
*/
var SITE_CONFIG = {
  "updated": "2026-10-29",
  "properties": {
    "suite": {
      "status": "open",
      "note": ""
    },
    "smarthome": {
      "status": "open",
      "note": ""
    }
  },
  "pricing": {
    "currency": "CAD",
    "suite": {
      "cleaningFee": 150,
      "maxGuests": 6,
      "defaultNightly": 319,
      "seasons": [
        {
          "name": "Winter",
          "from": "11-01",
          "to": "03-31",
          "nightly": 269
        },
        {
          "name": "Spring & fall",
          "from": "04-01",
          "to": "05-31",
          "nightly": 319
        },
        {
          "name": "Spring & fall",
          "from": "10-01",
          "to": "10-31",
          "nightly": 319
        },
        {
          "name": "June & September",
          "from": "06-01",
          "to": "06-30",
          "nightly": 359
        },
        {
          "name": "June & September",
          "from": "09-01",
          "to": "09-30",
          "nightly": 359
        },
        {
          "name": "Peak summer",
          "from": "07-01",
          "to": "08-31",
          "nightly": 429
        }
      ],
      "discounts": [
        {
          "minNights": 7,
          "pct": 15
        },
        {
          "minNights": 14,
          "pct": 25
        }
      ],
      "monthly": {
        "minNights": 30,
        "perNights": 30,
        "total": 5995
      }
    },
    "smarthome": {
      "cleaningFee": 175,
      "maxGuests": 8,
      "defaultNightly": 699,
      "seasons": [
        {
          "name": "Winter",
          "from": "11-01",
          "to": "03-31",
          "nightly": 599
        },
        {
          "name": "Spring & fall",
          "from": "04-01",
          "to": "05-31",
          "nightly": 699
        },
        {
          "name": "Spring & fall",
          "from": "10-01",
          "to": "10-31",
          "nightly": 699
        },
        {
          "name": "June & September",
          "from": "06-01",
          "to": "06-30",
          "nightly": 849
        },
        {
          "name": "June & September",
          "from": "09-01",
          "to": "09-30",
          "nightly": 849
        },
        {
          "name": "Peak summer",
          "from": "07-01",
          "to": "08-31",
          "nightly": 1099
        }
      ],
      "discounts": [
        {
          "minNights": 7,
          "pct": 15
        },
        {
          "minNights": 14,
          "pct": 25
        }
      ],
      "monthly": {
        "minNights": 28,
        "perNights": 30,
        "total": 17000
      }
    }
  },
  "analytics": {
    "goatcounter": "",
    "ga4": ""
  }
};
