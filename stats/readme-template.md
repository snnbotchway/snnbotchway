**Forward deployed engineer.** I join a team, learn its stack, and ship production software fast.

In ${surge_month} I rebuilt how I work. I run a fleet of coding agents on three machines and direct them through [T3 Code](https://github.com/pingdotgg/t3code) from my PC, phone or tablet. They share 40+ skills and switch to another model provider when one runs out. They check their own work: tests against real services, screenshots of every changed screen at phone and desktop size, and up to three independent review rounds with green CI before I merge. I write the specs and make the calls.

${prs_chart}

<sub>${partial_month_note}${private} of the ${prs} PRs since ${surge_month} went to ${private_projects} private projects.</sub>

Since ${surge_month}: **${prs}** PRs · **${repos}** repos · median **${median}** lines · 90th percentile **${p90}** · **${tests}%** tests

**Own projects**

- [Scrimly](https://github.com/snnbotchway/scrimly-case-study): tournament software for mobile esports, built solo and [live](https://scrimly.xyz). Teams register, upload match screenshots, and AI reads the scores into leaderboards; organisers pay through subscriptions.
- [faultline](https://github.com/snnbotchway/faultline): a complete frontend for self-hosted GlitchTip, covering issues, uptime, performance, logs, releases, alerts and settings.
- [django-entra-staff](https://github.com/snnbotchway/django-entra-staff): staff sign-in for Django with Microsoft Entra, passwords with a required authenticator code, and group-based access.

**Merged upstream**

- OpenZeppelin relayer: [Redis TLS support](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/674) and [unique IDs for Redis workers](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/892); in its SDK, [support for newer Node versions](https://github.com/OpenZeppelin/openzeppelin-relayer-sdk/pull/168)
- t3code: Chrome security fixes for the preview browser, [Chrome 156](https://github.com/pingdotgg/t3code/pull/27822) and [Chrome 157](https://github.com/pingdotgg/t3code/pull/30820)
- djoser: [rewrote the activation email template](https://github.com/sunscrapers/djoser/pull/731)

<details>
<summary>Lines written and PR sizes</summary>
<br>

${lines_chart}

Measure | Since ${surge_month}
--- | --:
[Lines written](${method_url}#lines-written), uncapped | ${written}
PRs of 1,000 lines or more | ${over_1k}
PRs of 5,000 lines or more | ${over_5k}

</details>

<sub>Updated ${updated} · <a href="${method_url}">How these numbers are counted</a></sub>
