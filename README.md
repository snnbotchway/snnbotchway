**Forward deployed engineer.** I join a team, learn its stack, and ship production software fast.

In September I rebuilt how I work around a fleet of coding agents, directed through [T3 Code](https://github.com/pingdotgg/t3code) from my PC, phone or tablet. I write the specs and make the calls. Changes pass tests against real services, phone and desktop screenshot checks on every changed screen, and up to three independent review rounds with green CI before I merge.

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/prs-dark.svg"><img src="assets/prs-light.svg" alt="Merged PRs per month by size: about 23 a month from May to August 2026, then 66 in September and 204 so far in November" width="560"></picture>

<sub>Counted to 15 November. 387 of the 434 PRs since September went to 15+ private projects.</sub>

Since September: **434** PRs across **20+** repos · half under **190** lines, 90% under **3,671** · **24%** of changed lines are tests · [a typical PR](https://github.com/snnbotchway/faultline/pull/22)

### Own projects

- [faultline](https://github.com/snnbotchway/faultline): a complete frontend for self-hosted GlitchTip, covering issues, uptime, performance, logs, releases, alerts and settings.
- [django-entra-staff](https://github.com/snnbotchway/django-entra-staff): staff sign-in for Django with Microsoft Entra, passwords with a required authenticator code, and group-based access.
- [Scrimly](https://github.com/snnbotchway/scrimly-case-study): tournament software for mobile esports that I built solo and ran in production. Teams registered, uploaded match screenshots, and AI read the scores into leaderboards; organisers paid through subscriptions.

### Merged upstream

- OpenZeppelin relayer: [Redis TLS support](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/674) and [unique IDs for Redis workers](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/892); in its SDK, [support for newer Node versions](https://github.com/OpenZeppelin/openzeppelin-relayer-sdk/pull/168)
- t3code: Chrome security fixes for the preview browser, [Chrome 156](https://github.com/pingdotgg/t3code/pull/27822) and [Chrome 157](https://github.com/pingdotgg/t3code/pull/30820)
- djoser: [rewrote the activation email template](https://github.com/sunscrapers/djoser/pull/731)

<details>
<summary>Lines shipped and PR sizes</summary>
<br>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/lines-dark.svg"><img src="assets/lines-light.svg" alt="Lines added and deleted per month, capped at 5,000 lines per PR: 141k added and 52k deleted so far in November" width="560"></picture>

Measure | Since September
--- | --:
[Lines shipped](https://github.com/snnbotchway/snnbotchway/blob/main/stats/README.md#lines-shipped), uncapped | 843k
PRs of 1,000 lines or more | 101
PRs of 5,000 lines or more | 31

</details>

<sub>Updated 15 Nov 2026 · <a href="https://github.com/snnbotchway/snnbotchway/blob/main/stats/README.md">How these numbers are counted</a></sub>
