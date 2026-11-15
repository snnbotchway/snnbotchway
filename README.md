**I'm a forward deployed engineer.** Drop me into your team and I'll learn the stack and get things into production fast.

In September I went all in on coding agents. I built my own setup around them and I run it from [T3 Code](https://github.com/pingdotgg/t3code) on my PC or my phone. I write the spec, the agents build it, and nothing gets merged until it's tested, reviewed (up to three times) and green on CI. That's the jump you see below.

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/prs-dark.svg"><img src="assets/prs-light.svg" alt="Merged PRs per month by size: about 23 a month from May to August 2026, then 66 in September and 205 so far in November" width="560"></picture>

<sub>Counted to 15 November.</sub>

Since September: **435** PRs in **20+** repos. Half are under **191** lines and 90% are under **3,671**. **24%** of the lines I change are tests. [Here's a typical one.](https://github.com/snnbotchway/faultline/pull/22)

### My best work is private

[**387** of those 435 PRs](https://github.com/snnbotchway/snnbotchway/blob/main/stats/README.md) went to 15+ private projects for my employer and clients, so I can't link any of it. Think internal systems a business runs on every day, payment and messaging tools, and DeFi backends. Email me at [solomonbotchway7@gmail.com](mailto:solomonbotchway7@gmail.com) and I'll walk you through it, as far as my NDAs allow.

### What I can show

- [faultline](https://github.com/snnbotchway/faultline): a better frontend for self-hosted GlitchTip. Issues, uptime, performance, logs, releases, alerts, the lot. I built it for the error tracking we run at work.
- [django-entra-staff](https://github.com/snnbotchway/django-entra-staff): staff sign-in for Django apps. Microsoft Entra, passwords that need an authenticator code, and access by group. Our internal apps at work sign in with it.
- [Scrimly](https://github.com/snnbotchway/scrimly-case-study): a tournament platform for mobile esports that I built on my own and ran in production. Teams uploaded their match screenshots and AI read the scores straight into the leaderboard.

### Merged upstream

- OpenZeppelin relayer: [Redis TLS support](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/674) and [unique IDs for Redis workers](https://github.com/OpenZeppelin/openzeppelin-relayer/pull/892), plus [newer Node support](https://github.com/OpenZeppelin/openzeppelin-relayer-sdk/pull/168) in the SDK. I needed all three for client work in production, so I added them upstream.
- t3code: kept the preview browser on the latest Chrome security fixes ([156](https://github.com/pingdotgg/t3code/pull/27822), [157](https://github.com/pingdotgg/t3code/pull/30820)).
- djoser: [rewrote the activation email](https://github.com/sunscrapers/djoser/pull/731).

<details>
<summary>Lines shipped and PR sizes</summary>
<br>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/lines-dark.svg"><img src="assets/lines-light.svg" alt="Lines added and deleted per month, capped at 5,000 lines per PR: 142k added and 52k deleted so far in November" width="560"></picture>

Measure | Since September
--- | --:
[Lines shipped](https://github.com/snnbotchway/snnbotchway/blob/main/stats/README.md#lines-shipped), uncapped | 844k
PRs of 1,000 lines or more | 101
PRs of 5,000 lines or more | 31

</details>

Hiring? Email me at [solomonbotchway7@gmail.com](mailto:solomonbotchway7@gmail.com).

<sub>Updated 15 Nov 2026 · <a href="https://github.com/snnbotchway/snnbotchway/blob/main/stats/README.md">How these numbers are counted</a></sub>
