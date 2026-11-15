**Forward deployed engineer.** I join a team, learn its stack, and ship production software fast.

In September I rebuilt how I work. I run a fleet of coding agents on three machines and direct them through [T3 Code](https://github.com/pingdotgg/t3code) from my PC, phone or tablet. They share 46 skills and switch to another model provider when one runs out. They check their own work: tests against real services, screenshots of every screen at phone and desktop size, and up to three independent review rounds with green CI before I merge. I write the specs and make the calls.

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/prs-dark.svg"><img src="assets/prs-light.svg" alt="Merged PRs per month by size: about 11 a month until August 2026, then 66 in September and 203 so far in November" width="560"></picture>

<sub>November counts to the 15th. 388 of the 434 PRs since September went to 15+ private projects.</sub>

Since September: **434** PRs · **23** repos · median **190** lines · 90th percentile **3,671** · **24%** tests

**Own projects**

- [faultline](https://github.com/snnbotchway/faultline): a complete frontend for self-hosted GlitchTip, covering issues, uptime, performance, logs, releases, alerts and settings.
- [django-entra-staff](https://github.com/snnbotchway/django-entra-staff): staff sign-in for Django with Microsoft Entra, passwords with a required authenticator code, and group-based access.
- [gbpc](https://github.com/snnbotchway/gbpc): a stablecoin system.

**Merged upstream**

- OpenZeppelin relayer: [Redis TLS support](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/674) and [unique IDs for Redis workers](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/892); in its SDK, [support for newer Node versions](https://github.com/OpenZeppelin/openzeppelin-relayer-sdk/pull/168)
- t3code: Chrome security fixes for the preview browser, [Chrome 156](https://github.com/pingdotgg/t3code/pull/27822) and [Chrome 157](https://github.com/pingdotgg/t3code/pull/30820)
- djoser: [rewrote the activation email template](https://github.com/sunscrapers/djoser/pull/731)

<details>
<summary>Lines written and PR sizes</summary>
<br>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/lines-dark.svg"><img src="assets/lines-light.svg" alt="Lines added and deleted per month, capped at 5,000 lines per PR" width="560"></picture>

Measure | Since September
--- | --:
[Lines written](https://github.com/snnbotchway/snnbotchway/blob/main/stats/README.md#lines-written), uncapped | 843k
PRs over 1,000 lines | 101
PRs over 5,000 lines | 31

</details>

<sub>Updated 15 Nov 2026 · <a href="https://github.com/snnbotchway/snnbotchway/blob/main/stats/README.md">How these numbers are counted</a></sub>
