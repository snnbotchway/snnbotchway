**Forward deployed engineer.** I join a team, learn its stack, and ship production software fast.

In ${surge_month} I rebuilt how I work around a fleet of coding agents, directed through [T3 Code](https://github.com/pingdotgg/t3code) from my PC, phone or tablet. I write the specs and make the calls. Changes pass tests against real services, phone and desktop screenshot checks on every changed screen, and up to three independent review rounds with green CI before I merge.

${prs_chart}

<sub>Counted to ${counted_to}. ${private} of the ${prs} PRs since ${surge_month} went to ${private_projects} private projects.</sub>

Since ${surge_month}: **${prs}** PRs across **${repos}** repos · half under **${median}** lines, 90% under **${p90}** · **${tests}%** of changed lines are tests · [a typical PR](https://github.com/snnbotchway/faultline/pull/22)

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

${lines_chart}

Measure | Since ${surge_month}
--- | --:
[Lines shipped](${method_url}#lines-shipped), uncapped | ${shipped}
PRs of ${large_floor} lines or more | ${large}
PRs of ${extra_large_floor} lines or more | ${extra_large}

</details>

<sub>Updated ${updated} · <a href="${method_url}">How these numbers are counted</a></sub>
