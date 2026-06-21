# Notification Service

## About the process 
### compare the first screening-task to homework task
I must tell that when I heard about reviewing the same tasks but this time with agents I thought OK the result should be the same.
Last time I didnt define Skills/MCPs/Plugins and after learning the materials I did so and much more then it helps the agent to be focus
on the Task it helps me. I better understood what I want and How to require from the agent to do so.
all the plan before with 2 agents and me go over. it organized my thoughts and help agent to be clear and specific
In the plan there were some insights that can be taken in several directions and if I would trust completly in the AI that would be problem
I think also that there were some edge cases which the agent didnt bring me in the last task and now it consider it 
another advantage is that the agent go over the code several times and it help him to find things He couldnt find in first time by coding.
I saw that if I prompt him to make long and complex task he made it worse then focused one.
For example I told to the first agent to go build PLAN.md page and it was stuck and couldnt complete the task so I reapet the demand again and again
and then I Realized that maybe it has connection to the context that the agent can do (I actually saw that the context is about to finish)
So I Opened new agent and brought it the task and it completed the task quickly

## Language
I chose python because I wanted to challenge myself - python is my unfamilier language

### Context & Instructions
The part of adding MCPs and hooks/plugins/skills to project was intresting part 
I enjoy to explore what are the options and to match the specific need to my project
The list of services I used:
context7  @modelcontextprotocol/server-github @modelcontextprotocol/server-memory  code-reviewer.md  code-simplifier.md  comment-analyzer.md pr-test-analyzer.md
silent-failure-hunter.md  type-design-analyzer.md  pr-review-toolkit  block_provider_edits.py (preToolUse hook)  guard_git_push.py (beforeShellExecution hook)

session_context.py (sessionStart hook)
### Process — plan before code
This is critical stage that I dont unserstand How did I manage until today without doing it
It helps for future mistakes that you unserstand A the agent B and when you get the code you need to explore what was the conflict
I also like that the agent define to himself phases in order the task will be easier to complete

### Implementation
That was more or less like I did in last project I manage branches and go over the code of agent to see he doesnt make any mistakes

### Verification — you own "done"
Last time I didnt use automatic tests so I checked the edge cases then saw there is a mistake then told the agent fix this specific mistakes
This time with the automatic tests the agent did It saved me half job to do
After these tests for sure i tested also by myself (using postman) in order to see everything is good and up to date


