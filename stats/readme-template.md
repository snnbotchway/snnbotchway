**I'm a forward deployed engineer.** Drop me into your team and I'll learn the stack and get things into production fast.

In ${surge_month} I went all in on coding agents. I built my own setup around them and I run it from [T3 Code](https://github.com/pingdotgg/t3code) on my PC or my phone. I write the spec, the agents build it, and nothing gets merged until it's tested, reviewed (up to three times) and green on CI. That's the jump you see below.

${prs_chart}

<sub>Counted to ${counted_to}. ${private} of the ${prs} PRs since ${surge_month} were private work across ${private_projects} projects, so you only get the totals.</sub>

Since ${surge_month}: **${prs}** PRs in **${repos}** repos. Half are under **${median}** lines and 90% are under **${p90}**. **${tests}%** of the lines I change are tests. [Here's a typical one.](https://github.com/snnbotchway/faultline/pull/22)

### Own projects

- [faultline](https://github.com/snnbotchway/faultline): a better frontend for self-hosted GlitchTip. Issues, uptime, performance, logs, releases, alerts, the lot.
- [django-entra-staff](https://github.com/snnbotchway/django-entra-staff): staff sign-in for Django apps. Microsoft Entra, passwords that need an authenticator code, and access by group.
- [Scrimly](https://github.com/snnbotchway/scrimly-case-study): a tournament platform for mobile esports that I built on my own and ran in production. Teams uploaded their match screenshots and AI read the scores straight into the leaderboard.

### Merged upstream

- OpenZeppelin relayer: added [Redis TLS support](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/674) and [unique IDs for Redis workers](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/892), plus [newer Node support](https://github.com/OpenZeppelin/openzeppelin-relayer-sdk/pull/168) in the SDK.
- t3code: kept the preview browser on the latest Chrome security fixes ([156](https://github.com/pingdotgg/t3code/pull/27822), [157](https://github.com/pingdotgg/t3code/pull/30820)).
- djoser: [rewrote the activation email](https://github.com/sunscrapers/djoser/pull/731).

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
