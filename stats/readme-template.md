Forward deployed engineer. I join a team, learn its stack and ship production software fast.

I've shipped with coding agents since December 2025. In ${surge_month} I rebuilt my agent fleet and how I work with it: I write the specs, agents build, and every PR gets up to three independent review rounds and green CI before I merge.

${prs_chart}

<sub>${partial_month_note}${private} of the ${prs} PRs since ${surge_month} went to ${private_repos} private projects, shown as totals only.</sub>

Since ${surge_month}: **${prs}** PRs · **${repos}** repos · median **${median}** lines · 90th percentile **${p90}** · **${tests}%** tests

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

${lines_chart}

Measure | Since ${surge_month}
--- | --:
[Lines written](${method_url}#lines-written), uncapped | ${written}
Median PR | ${median} lines
90th percentile PR | ${p90} lines
PRs over 1,000 lines | ${over_1k}
PRs over 5,000 lines | ${over_5k}
Share of lines that are tests | ${tests}%

</details>

<sub>Updated ${updated} · <a href="${method_url}">How these numbers are counted</a></sub>
