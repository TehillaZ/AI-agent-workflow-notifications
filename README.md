# AI-First Engineering Workflow: Notifications API
<img width="2560" height="840" alt="banner" src="https://github.com/user-attachments/assets/dcd85ec2-80ac-440f-afdc-b179e67f1259" />
## Background

This project was part of the **AI Engineering track at ZioNet**. The exercise was built like a real
screening assignment: take an existing notifications API (email, SMS and push), find its issues and
improve it, working **AI-first** with coding agents.
My work was selected to be presented to the full ZioNet cohort (~60 participants).

The goal was not only to fix the code, but to learn how to work with AI agents in a controlled way:
plan before coding, split work between agents, and verify everything they produce.

**What I built on top of Cursor:**
- **Custom review agents:** code reviewer, code simplifier, comment analyzer, PR test analyzer,
  silent-failure hunter and type-design analyzer
- **Skills:** a PR review toolkit and a skill for creating new hooks
- **Hooks:** block edits to the provider files (treated as external vendors), scan for secrets before
  every `git push`, and inject project rules into every new agent session
- **MCP servers:** GitHub, memory and context7

**How I worked:** one agent wrote the plan (`PLAN.md`), I reviewed it and resolved its open questions,
a second agent reviewed the code, and I approved every change. Tests were written first and run
automatically (pytest), and I also checked the API manually with Postman.

> The course rules required the README notes below to be written by hand, without AI.
> They are kept exactly as I wrote them during the course.

## My process and reflections (original notes)
## About the process 
### Comparing the First Task to the Homework Task
Last time I didnt define Skills/MCPs/Plugins and after learning the materials I did so and much more then it helps the agent to be focus
on the Task it helps me. I better understood what I want and How to require from the agent to do so.<br>
The plan part before with 2 agents and me go over organized my thoughts and help agent to be clear and specific.<br>
In the plan there were some insights that can be taken in several directions and if I would trust completly in the AI that would be problem.<br>
I think also that there were some edge cases which the agent didnt noticed in the last task and now it consider it.<br>
another advantage is that the agent go over the code several times and it help him to find things It couldnt find in first time by coding.<br>
I saw that if I prompt him to make long and complex task he made it worse then focused one.<br>
For example I told to the first agent to go build PLAN.md page and it was stuck and couldnt complete the task so I repeat the demand again and again
and then I Realized that maybe it has connection to the context that the agent can do (I actually saw that the context is about to finish)
So I Opened new agent and brought it the task and it completed the task quickly.<br>

## Language
I chose python because I wanted to challenge myself - python is my unfamiliar language

### Context & Instructions
I expanded AGENTS.md and match it to my needs I let the model to go over the code and keep is first conclusions in NOTES.md<br>
I copy the content of the email and told the agent to build me SPEC.md page.<br>
The part of adding MCPs and hooks/plugins/skills to project was the intresting part 
I enjoy to explore what are the options and to match the specific need to my project.  

The list of services I used:
- context7 - it keeps the model context narrow and clear
- @modelcontextprotocol/server-github - it help the model to connect github safetly and upload the code
- @modelcontextprotocol/server-memory - it good for the model to keep important info.
I wanted to use it in order to keep the instructions (not to update providers or README)
- code-reviewer.md - best practices before the code run to production
- code-simplifier.md - it is good for maintainable I used it in the code in `_min_segments_from`
- comment-analyzer.md - analyze comments and check the list of TODOs if they are all done
- pr-test-analyzer.md - checks the validition of tests
- silent-failure-hunter.md - ensure that there are no silent failtures (like empty catch)
- type-design-analyzer.md - ensure the architacture of Types/Interfaces to prevent runtime errors
- pr-review-toolkit - helps to pull-request to the main branch I used some PR in the project
- block_provider_edits.py (preToolUse hook) - ensure that there are no changes in the files which are not allowed (like providers)
- guard_git_push.py (beforeShellExecution hook) - before pushing to git auto test ensure there are no api-keys or other secrets
- session_context.py (sessionStart hook) - this inject in a new session project boundaries, house rules, and current memory contexts to the agent

### Process — plan before code
The process was like that - The first agent read the code and bring PLAN.md I went over the code change a little bit and answer to It's conflicts<br>
Then I let to second agent to review the code and he make his changes and the I approval the last result<br>
It helps for future mistakes that you understand in one way but the agent might approach it completely differently and when you get the code the result is
nothing like what I expected<br>
I also like that the agent define to himself phases in order the task will be easier to complete

### Implementation
That was more or less like I did in last project I manage branches and review the code of agent to see it doesnt make any mistakes<br>
I didnt notice to repeating tasks so I didnt make new skill

### Verification — you own "done"
I told the agent first to make fail-test then to solve and then again to make test and see it was successful (TDD)<br>
Last time I didnt use automatic tests so I checked the edge cases then saw there is a mistake then told the agent fix these specific mistakes<br>
This time with the automatic tests the agent did, It saved me half job to do.<br>
After these tests for sure I tested also by myself (using postman) in order to see everything is good and up to date


