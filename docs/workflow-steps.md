# NeuroNAV: Skill Development Workflow

## Phase 1: Skill Authoring (Week 1)

### Step 1: Write the Skill File
Each skill lives in `.claude/skills/<module-name>/SKILL.md` with YAML frontmatter.

```yaml
---
name: skill-name
description: One-line description
type: skill
triggers:
  - "keyword phrases that activate this skill"
---
```

The body contains the full system prompt: identity, rules, response patterns, adaptation logic, and examples.

### Step 2: Claude A / Claude B Testing Pattern

This is the core development loop:

1. **Claude A** (development session): You write/edit the SKILL.md file
2. **Claude B** (separate Claude Code session): You test the skill by roleplaying as a user
3. **Evaluate**: Does Claude B follow the skill instructions? Does it feel right?
4. **Iterate**: Back to Claude A to refine based on what you observed

```
┌─────────────┐     write      ┌──────────────┐
│  Claude A    │ ──────────────>│  SKILL.md    │
│  (author)    │ <──────────────│  (skill file)│
└─────────────┘     refine     └──────┬───────┘
                                       │ loads
                                       v
                               ┌──────────────┐
                               │  Claude B    │
                               │  (test agent)│
                               └──────────────┘
                                       │
                                       v
                               ┌──────────────┐
                               │  Evaluation  │
                               │  (human)     │
                               └──────────────┘
```

### Step 3: Context Management
- Start a FRESH Claude Code session for each module (prevents context bleed)
- Use the Explore > Plan > Implement > Commit workflow
- Keep skill files under 2000 words — if longer, split into sub-skills

---

## Phase 2: Profile & RAG Setup (Week 1-2)

### Step 4: User Profile Schema Design
1. Define the JSON schema (see profile-manager SKILL.md)
2. Build progressive intake questions (Phase 1 → 2 → 3)
3. Test with 3+ diverse user personas
4. Validate that the schema captures all information other modules need

### Step 5: RAG Knowledge Base Population
Upload to CollaborAITE's RAG system:

| Document Type | Chunking Strategy | Chunk Size | Metadata |
|--------------|------------------|------------|----------|
| Rubrics | Per criterion row | 100-300 tokens | course_id, assignment, criterion, weight |
| Syllabi | Section-based recursive | 300-500 tokens | course_id, section_type, dates |
| Conversation logs | Speaker-turn-based | 200-400 tokens, 20-50% overlap | timestamp, topic, sentiment |
| User profiles | NEVER chunk | Full document | user_id |
| Class slides | Per slide | 200-500 tokens | course_id, lecture_number, slide_number |

**Critical rule**: Always prepend contextual headers before embedding:
```
"Document: ENG101 Essay Rubric | Type: Rubric | Course: ENG101 | Assignment: Midterm Essay"
```

### Step 6: Mandatory Profile Injection
Configure the system so the user's full profile is ALWAYS injected into the LLM context — never rely on similarity search to find it.

---

## Phase 3: Module Integration (Week 2-3)

### Step 7: Router Configuration
1. Implement intent classification in the router skill
2. Test with 20+ diverse user messages to validate routing accuracy
3. Add fallback behavior for ambiguous intents
4. Configure context-passing JSON structure between router and modules

### Step 8: Cross-Module Testing
Test these multi-module flows:

| Flow | Modules Involved | Test Scenario |
|------|-----------------|---------------|
| New user → first assignment | Profile Manager → Assignment Decoder | User onboards then immediately asks about a rubric |
| Weekly planning | Schedule Builder → Strategy Recommender | User asks for a schedule, then gets stuck on a task |
| Event prep → debrief | Social Prep → Wellbeing Monitor | User preps for presentation, comes back drained |
| Burnout detection → intervention | Wellbeing Monitor → Strategy Recommender | Monitor flags burnout, recommends load reduction |
| Assignment → scheduling | Assignment Decoder → Schedule Builder | Decoder breaks down steps, Builder schedules them |

### Step 9: Conversation Continuity Testing
Verify across sessions:
- Profile information persists and is used correctly
- Strategy history is tracked (don't re-recommend failures)
- Pattern detection works across 5+ sessions
- Schedule adjustments carry forward

---

## Phase 4: Evaluation (Week 3-4)

### Step 10: Internal Quality Checks

Run each skill through this checklist:

- [ ] Follows the 10 core interaction rules
- [ ] Uses strengths-affirming language (no deficit framing)
- [ ] Respects the 150-word message limit
- [ ] Asks only one question per message
- [ ] Provides progressive disclosure
- [ ] Adapts to user profile
- [ ] Includes orientation markers (Step X of Y)
- [ ] Offers choices, not mandates
- [ ] Never pathologizes
- [ ] Crisis escalation works correctly

### Step 11: Persona-Based Testing

Test with all 5 example user personas (see examples/user-profiles/):
1. Does the agent adapt communication style to each persona?
2. Does it reference the right strategies for each profile?
3. Does it correctly calibrate granularity (spiciness)?
4. Does it avoid re-recommending strategies marked as failed?

### Step 12: User Evaluation (Mini-Study)

**Protocol** (60-90 min per participant, 2-3 neurodivergent users):

1. Pre-session questionnaire (5 min)
2. Four task scenarios (25 min):
   - "Plan a research paper due in 2 weeks while you have an exam in 10 days"
   - "You can't start an assignment — ask for help"
   - "Check when your next assignment is due"
   - "Tell NeuroNAV you're feeling overwhelmed"
3. Semi-structured interview (25 min)
4. Post-session questionnaire (5 min)

**Environment accommodations**:
- Quiet, low-sensory room
- Adjustable lighting
- Fidget tools available
- Break offers every 20 min
- Written agenda provided upfront
- "You can stop at any time for any reason"

**Analysis**: Qualitative thematic analysis (not inferential stats with 2-3 participants)

---

## Phase 5: Iteration & Refinement (Ongoing)

### Step 13: Pattern Library Updates
After each user session, update:
- Strategy effectiveness data
- New jargon translations discovered
- Script templates that worked well
- Check-in phrasings that landed

### Step 14: Scaffolding Reduction
Build in progressive independence:
- Track whether users initiate fewer help requests over time
- Periodically prompt: "Want to try planning your week on your own first?"
- Celebrate autonomous wins: "You handled that without needing a breakdown — nice."

### Step 15: DSPy Optimization (Post-Launch)
Once you have 50+ real conversations:
1. Extract input-output pairs from successful interactions
2. Use DSPy to optimize prompts against quality metrics
3. A/B test optimized vs. hand-crafted prompts
4. Iterate on the modules with highest variance
