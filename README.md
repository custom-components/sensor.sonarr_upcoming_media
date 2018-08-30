# Sonarr Upcoming Media Component

Component required to use the associated Lovelace card: [Upcoming_Media_Card](https://github.com/custom-cards/upcoming-media-card)</br>
This is just a modified version of home assistants default sonarr component.</br>
This component works with or without the default sonarr component.</br></br>
<link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/FgwNR2l"><img src="https://www.buymeacoffee.com/assets/img/BMC-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px">If you feel I deserve it, you can buy me a coffee</span></a>

## Installation:

1. Install this component by copying to your `/custom_components/sensor/` folder.
2. Add this to your `configuration.yaml` using the config options below example. 
3. **You will need to restart for the component to start working.**

```yaml
sensor:
- platform: sonarr_upcoming_media
  api_key: YOUR_API_KEY
  host: 192.168.1.4
  port: 8989
  days: 2
  ssl: true
```

### Options

| key | default | required | description
| --- | --- | --- | ---
| api_key | | yes | Your Sonarr API key
| host | localhost | no | The host Sonarr is running on.
| port | 8989 | no | The port Sonarr is running on.
| urlbase | / | no | The base URL Sonarr is running under.
| days | 7 | no | How many days to look ahead for the upcoming sensor, 1 means today only.
| ssl | False | no | Whether or not to use SSL for Sonarr. Set to `True` if you use SSL.
