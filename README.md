# Sonarr Upcoming Media Component

Home Assistant component to feed [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card) with
Sonarr's upcoming releases.</br>
This component does not require, nor conflict with, the default Sonarr component.</br></br>
### Issues
Read through these two resources before posting issues to GitHub or the forums.
* [troubleshooting guide](https://github.com/custom-cards/upcoming-media-card/blob/master/troubleshooting.md)
* [@thomasloven's lovelace guide](https://github.com/thomasloven/hass-config/wiki/Lovelace-Plugins).

## Installation:

1. Install this component by copying [these files](https://github.com/custom-components/sensor.sonarr_upcoming_media/tree/master/custom_components/sonarr_upcoming_media) to `/custom_components/sonarr_upcoming_media/`.
2. Install the card: [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card)
3. Add the code for the card to your `ui-lovelace.yaml`. 
4. **You will need to restart after installation for the component to start working.**

### Adding device
To add the **Sonarr Upcoming Media** integration to your Home Assistant, use this My button:

<a href="https://my.home-assistant.io/redirect/config_flow_start?domain=sonarr_upcoming_media" class="my badge" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg"></a>

<details><summary style="list-style: none"><h3><b style="cursor: pointer">Manual configuration steps</b></h3></summary>

If the above My button doesn’t work, you can also perform the following steps manually:

- Browse to your Home Assistant instance.

- Go to [Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations/).

- In the bottom right corner, select the [Add Integration button.](https://my.home-assistant.io/redirect/config_flow_start?domain=sonarr_upcoming_media)

- From the list, select **Sonarr Upcoming Media**.

- Follow the instructions on screen to complete the setup.
</details>

**Do not just copy examples, please use config options above to build your own!**

### Sample for ui-lovelace.yaml:

    - type: custom:upcoming-media-card
      entity: sensor.sonarr_upcoming_media
      title: Upcoming TV
      
      
### Card Content Defaults:

| key | default | example |
| --- | --- | --- |
| title | $title | "The Walking Dead" |
| line1 | $episode | "What Comes After" |
| line2 | $release | "Mon, 10/31 9:00pm" if it's more than a week away or "Monday, 9:00pm" if it's within a week.|
| line3 | $rating - $runtime | "★ 7.8 - 45 min" |
| line4 | $number - $studio | "S06E09 - AMC"
| icon | mdi:arrow-down-bold | https://materialdesignicons.com/icon/arrow-down-bold
