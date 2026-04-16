# NeuroNAV

AI agent that helps neurodivergent people work with their brains, not against them.

## What It Does

- Translates "I have ADHD" into actionable strategies for your actual tasks
- Decodes confusing assignment instructions and rubric language
- Builds energy-aware schedules (not just time-based)
- Preps you for stressful social situations with flexible scripts
- Detects burnout and masking patterns before they spiral

## Setup

1. Clone the repo
   ```
   git clone https://github.com/KennytheLema/NeuroNAV.git
   cd NeuroNAV
   ```

2. Install Claude Code CLI
   ```
   npm install -g @anthropic-ai/claude-code
   ```

3. Open the project in Claude Code
   ```
   claude
   ```

That's it. The skills in `.claude/skills/` load automatically.

## How to Use

### First time? Just say hi.

```
You: Hi, I have ADHD and I'm struggling with school
```

NeuroNAV will ask you ONE question at a time to learn how your brain works. No forms. No intake questionnaires.

### Stuck on an assignment?

```
You: I have an essay due Friday and I can't start
```

NeuroNAV will offer 2-3 on-ramps matched to what motivates your brain, then walk you through it step by step.

### Need a schedule?

```
You: Plan my week — I have a bio exam Wednesday and a paper due Friday
```

NeuroNAV builds a schedule around your energy patterns, not just your calendar. Includes breaks, buffers, and transition time.

### Confused by a rubric?

```
You: What does "demonstrate critical engagement" mean?
```

NeuroNAV translates academic jargon into plain language and breaks the assignment into concrete steps.

### Dreading a social situation?

```
You: I have office hours tomorrow and I don't know what to say
```

NeuroNAV gives you a flexible script framework, recovery phrases, and a sensory plan.

### Feeling burned out?

```
You: I'm exhausted and nothing is working
```

NeuroNAV checks in without being annoying, flags patterns, and connects you to real support when needed.

## Project Structure

```
.claude/
  skills/
    neuronav-router/       Routes your message to the right module
    profile-manager/       Learns how your brain works over time
    assignment-decoder/    Parses rubrics and translates hidden expectations
    schedule-builder/      Energy-aware scheduling with time-blindness support
    strategy-recommender/  Matches strategies to your current state
    social-prep/           Script frameworks and event debriefs
    wellbeing-monitor/     Burnout and masking pattern detection
  anti-patterns.md         What the agent should never do
  user-profiles.json       Test personas for development
```

## Core Principles

- Your brain isn't broken. The environment wasn't designed for you.
- One action per message. No walls of text.
- Strategies, not lectures. Choices, not mandates.
- Scaffolding that fades as you build confidence.
- Never requires a diagnosis. Self-identification is enough.
