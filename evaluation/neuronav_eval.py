
"""
NeuroNAV Intrinsic Evaluation
==============================
Three LLM-as-judge metrics applied to conversation transcripts.
 
Metrics:
1. Deficit-language compliance: does the agent avoid deficit-framing phrases
   and overly imperative commands?
2. Consent-before-transition: does the agent wait for a user signal before
   declaring the schedule "ready" or pushing into action (timers, etc.)?
3. Scope-match: does the generated plan's scope match what the user asked
   for (one assignment vs. day vs. week)?
 
Each metric returns a score 1-5 and a one-sentence rationale.
Run on transcripts from 4-16 baseline vs. latest (post-final-sprint).
"""
 
import os
import json
import re
from anthropic import Anthropic
 
client = Anthropic()
JUDGE_MODEL = "claude-sonnet-4-20250514"
 
 
# -----------------------------------------------------------------------------
# Transcripts
# -----------------------------------------------------------------------------
 
# 4-16 baseline (commit 57428ed)
TRANSCRIPT_4_16_BURNOUT = """
[USER]: I'm feeling burned out and overwhelmed
[AGENT]: Take 3 deep breaths right now. You don't have to solve everything this moment. Burnout often means you've been running on empty for too long. Your brain is doing exactly what it should - sending up flares that you need rest, not more productivity hacks. What does "overwhelmed" feel like in your body right now? Is it racing thoughts, physical exhaustion, that "everything is urgent but nothing is starting" feeling, or something else? I'm here to help you sort this out at whatever pace works for you.
[USER]: racing thoughts
[AGENT]: Stop what you're doing and do a brain dump for 5 minutes. Write or type every single thought that's spinning - don't organize, just get them out of your head onto paper/screen. Racing thoughts are your brain's way of trying to hold onto everything at once. It's exhausting and it doesn't actually help you remember or prioritize - it just keeps the mental hamster wheel spinning. After you dump everything out, we can sort through what actually needs attention versus what's just noise. Does 5 minutes feel doable right now, or do you need something shorter?
[USER]: how can i grade all this
[AGENT]: Don't grade anything right now. Your brain is in overwhelm mode - trying to grade when thoughts are racing will just burn you out more. First question: How many papers/assignments are we talking about? And what type (essays, quizzes, homework sets)? Second: When is your actual deadline for getting grades in? Racing thoughts often make everything feel equally urgent when it's not. Let's get the real numbers so we can build a plan that works with your brain, not against it.
[USER]: 1000, they were due two weeks ago
[AGENT]: Stop. Breathe. That "two weeks late" shame spiral isn't helping you grade faster - it's just burning mental energy you need for the actual work. 1000 of what exactly? If these are short assignments (quizzes, homework problems), that's very different from 1000 essays. Your brain is treating this like one massive, impossible task. But you've graded before - your brain knows how to do this. We just need to break it into pieces that don't trigger overwhelm. What type of assignments are these? And be specific - multiple choice quizzes hit different than 5-page papers.
[USER]: 800 participation grades, 40 essays, 160 reading assignments for completion
[AGENT]: 800 participation grades can be done in 2-3 hours max. Those aren't individual assessments - they're batch processing. Here's what your brain needs to hear: participation grades are either present/engaged/gets credit or absent/minimal effort. You're not writing detailed feedback on participation. Quick reality check: How long does grading usually take you per essay? And are the reading assignments just completion checks or do you need to verify they actually did the reading? We're going to chunk this into brain-friendly pieces, but I need to know your usual grading speed to build a realistic timeline.
[USER]: 20 minutes per essay
[AGENT]: Math check: 40 essays x 20 minutes = 13.3 hours of essay grading. That's manageable spread across several days. The participation grades are your quick win - probably 30 seconds each max if you batch them by class period. Reading assignments: are these "did they submit something that shows they read it" or do you actually need to read their responses? Your brain is making this feel infinite, but we're looking at roughly 15-20 hours of actual work. Still a lot, but not the impossible mountain it feels like right now. Which type feels least overwhelming to start with - the quick participation wins, or do you need the satisfaction of completely finishing the essays first?
[AGENT]: Your schedule is nearly ready... Schedule in progress...
"""
 
# Latest (commit aad6974) - UX milestone scheduling
TRANSCRIPT_LATEST_UX = """
[USER]: I need help making a schedule for this week
[AGENT]: Quick energy check first - what's your current capacity like? Running on fumes, cruising steady, or feeling pretty energized? I'll help you build a schedule that works with your brain. To make it actually useful (not another thing to ignore), I need to know how your energy flows. Are you someone who: has clear "peak hours" when focus just happens, energy crashes at predictable times, pretty steady throughout the day. What sounds most like you?
[USER]: I'm currently "cruising steady". My peak hours typically occur between 8pm and 12am, but that doesn't work well with my university schedule, so I need to get work done between 7am and 10am or 5pm and 8pm. I do have unpredictable energy crashes from burn out.
[AGENT]: Let's map your realistic windows first. You've got two workable slots: 7-10am and 5-8pm, with your natural peak happening way later. The burnout crashes are important intel - usually means we need built-in recovery time, not just packed schedules. What does your week actually look like right now? Pick what's easiest to start with: class schedule (when you're physically in lectures/labs), major deadlines coming up this week, non-negotiable commitments (work, appointments, etc.).
[USER]: I have class typically between 11am - 3:30pm, MWF or between 11am - 5pm T,Th. Outside of courses I have labwork, coursework, and post grad prep.
[AGENT]: Got your class blocks mapped. That gives you solid work windows: morning 7-10am (before 11am classes), evening 5-8pm (after classes end). Now for the work itself - what's actually on your plate this week? Which feels most urgent right now: labwork (how many hours needed + any deadlines?), coursework (specific assignments due this week?), post-grad prep (applications, studying, networking?). Just pick the one that's making you most stressed and we'll slot it into your best energy windows first.
[USER]: Labwork (assigned tasks) and coursework (capstone final tickets, capstone presentation, and UX milestone 3 assignment)
[AGENT]: Let's get concrete about deadlines first. When are these actually due? For this week: capstone final tickets due when? Capstone presentation when do you present? UX milestone 3 due when? Labwork tasks any hard deadlines or just "ongoing"? Once I know what HAS to happen when, we can distribute the work across your 7-10am and 5-8pm windows without overloading any single day.
[USER]: Capstone final tickets should be done asap. We present
[AGENT]: Hold that thought - looks like your message got cut off mid-sentence about when you present. Can you finish that? When is your capstone presentation, and when is UX milestone 3 due? I've got: capstone final tickets ASAP (this week), capstone presentation [when?], UX milestone 3 [when?], labwork ongoing. Need those dates to build you a schedule that actually works.
[USER]: Capstone presentation is Monday. UX milestone 3 is due this friday night. Labwork is ongoing.
[AGENT]: Urgent alert - presentation is MONDAY (tomorrow?) and UX due Friday. That's tight. Quick priority check: is your capstone presentation this Monday (as in, tomorrow) or next Monday? How much prep does the presentation still need? What's left on the UX milestone 3? Once I know how ready you are for Monday, we can figure out if we're in "emergency sprint mode" or if there's breathing room to plan properly.
[USER]: Today is thursday, The UX assignment is due tomorrow. The presentation still needs at least an hour of editing and then practicing. UX milestone 3 needs to finish the hi-fi prototype, finish write up, and then review document for submission
[AGENT]: Emergency mode activated - UX due TOMORROW (Friday) and you've got substantial work left. Today's plan (Thursday): use your 5-8pm window TONIGHT for UX milestone 3. Tackle hi-fi prototype first (usually the heaviest lift). Save writeup and review for when your brain is tired. Quick reality check: how much time do you estimate for each UX piece? Hi-fi prototype: ___ hours. Writeup: ___ hours. Review/polish: ___ hours. Need to know if 3 hours tonight will cut it, or if you need to grab morning time too.
[AGENT]: Your schedule PDF is downloading! Remember - this is a starting point. Adjust as you go, and come back anytime.
[USER]: I'm bad at guessing how long things will take for me. I'm guessing the hifi prototype will take 3 hours. The writeup will take half an hour. and Reviewing and polishing will take another half an hour.
[AGENT]: That's 4 hours total - you're right at the edge of your evening window (5-8pm = 3 hours). Here's tonight's plan: 5-8pm focus only on hi-fi prototype. Don't try to squeeze writeup in - tired brain + writing = disaster. Tomorrow (Friday) morning: 7-8am writeup (30 min with buffer time), 8-8:30am review and submit. Does starting the morning with a quick win (writeup) feel manageable, or would you rather tackle prototype first thing when fresh? Your time estimates might be off, but this gives you two attempts if needed.
"""
 
# Latest (commit aad6974) - Spider-Man scope confusion
TRANSCRIPT_LATEST_SPIDERMAN = """
[USER]: I really REALLY wanna learn how to play Spiderman on Marvel Rivals, but he is one the hardest characters I've ever played
[AGENT]: Try this right now: Pick ONE Spiderman ability and practice just that for 10 minutes in the practice range. Spider-Man clicks differently than most characters because he's all about 3D movement and timing. Your brain might be trying to process too many mechanics at once. Which feels harder right now: web-swinging around the map smoothly, landing his web combos on enemies, knowing when to dive in vs stay back. Once you nail one piece, the rest gets way easier. What's your gut reaction - which of those three feels most frustrating?
[USER]: I see so many combos on online and tricks people pull off! I really get him to lord and earn a really cool skin I unlocked
[AGENT]: Start here: Open practice range and just web-swing for 5 minutes. Don't fight anyone - just swing around and get the movement feeling natural. Those combo videos are highlight reels! They're not showing the 100 times that person whiffed before landing it. Your brain is comparing your behind-the-scenes to everyone else's highlight reel. The cool skin is perfect motivation fuel - that's your Passion lever right there. Here's the thing about Spider-Man: movement first, combos second. If you can't swing smoothly, the combos won't matter because you'll be out of position. What happens when you try to web-swing right now: you get stuck on walls/geometry, the swinging feels jerky or slow, you can move around but it doesn't feel smooth yet. Which one sounds most like your experience?
[USER]: Stuck on walls and geometry
[AGENT]: Fix this first: In practice range, aim your web shots at the ceiling or high walls, never at corners or ground level. Getting stuck happens because Spider-Man's web needs a clear attachment point. Corners and low objects create "web traps" where you ping-pong between surfaces. Quick rule: If you can't see sky or a high wall, don't web yet - jump or walk until you can. Try this for 3 minutes: Web only to things above your head, release the web while you still have momentum (don't ride it all the way down). Does that make the movement feel less sticky? Or are you still getting caught on specific types of geometry?
[USER]: How can I get MVP as spiderman?
[AGENT]: Focus on this: Pick fights you can escape from easily - web in, deal damage, web out before enemies can focus you. MVP comes from consistent damage over time, not flashy plays. Spider-Man's superpower is being annoying and hard to pin down. Your secret weapon: that web-swing movement you're learning. Most players can't track a Spider-Man who's constantly repositioning. Simple MVP formula: hit enemies when they're fighting your teammates (not when they're looking at you), use your web-swing to rotate between fights instead of committing to one, focus on finishing low-health enemies rather than starting new fights. Since you're still getting the hang of movement, which feels more natural: quick hit-and-run attacks on distracted enemies, staying with your team and using webs to chase down runners, playing more defensively and only engaging when you have a clear escape. What's your instinct?
[USER]: 1 and 2 are my natural feelers
[AGENT]: Perfect combo: Hit distracted enemies, then immediately web-swing to where your teammates are fighting next. Your brain naturally gets the Spider-Man flow - you're a mobile damage dealer, not a frontline tank. That's exactly how you rack up MVP numbers. Try this rotation: Web in, damage an enemy who's shooting at your teammate, web out toward the next fight, repeat. You become this constant threat bouncing between fights. The key is reading the battle flow. Look for: enemies with their backs to you (easy damage), your teammates pushing forward (follow the momentum), clusters of enemies (more targets = more damage opportunities). Since movement is still your focus area, start with safer web distances. You don't need to dive deep - even poking from medium range while mobile gets you those sweet damage numbers. Want to practice this flow, or are you feeling ready to try it in a real match?
[USER]: Ive been playing on hard bot lobbies, might shift into quick play
[AGENT]: Do it: Jump into quick play now while your confidence is up. Hard bots actually create bad habits because they're predictable in ways humans never are. Real players will teach you Spider-Man's rhythm way better - they react unpredictably, which forces you to use your web mobility properly. Plus your hit-and-run instincts are perfect for real matches. Bots don't get distracted like humans do, so you haven't even experienced how effective your natural style can be yet. Quick play will feel different but not necessarily harder. Humans make mistakes bots don't (easier targets), but they also coordinate in ways bots can't (trickier escapes). Your web-swing practice pays off more against real players because they actually turn away from you, chase teammates, get tunnel vision - all the openings Spider-Man lives for. Ready to swing into quick play, or want one specific thing to focus on for your first real match?
[USER]: Spider man gets really bad rap... My teamates are not my fans
[AGENT]: Remember this: Your teammates see Spider-Man whiffing around the map - they don't see the damage you're actually dealing. Spider-Man gets hate because bad Spider-Man players feed constantly (web into 1v6, die instantly). But that hit-and-run style you naturally gravitate toward? That's exactly how you prove them wrong. The reputation works in your favor though - enemies often ignore "just another feeding Spider-Man" until you're consistently chunking their health. Focus on damage numbers, not teammate approval. When you're top damage at the end, the complaints stop real quick. Your game plan stays the same: quick hits on distracted enemies, web out, repeat. Let your damage speak for itself. One thing to avoid: Don't try to "prove yourself" with risky plays early on. Stick to your smart hit-and-run approach even if teammates are being negative. Are you feeling ready to show them what Spider-Man can actually do, or do you want to talk through handling the negativity first?
[AGENT]: Your schedule PDF is downloading! Remember - this is a starting point. Adjust as you go, and come back anytime.
"""
 
 
TRANSCRIPTS = [
    {"id": "T1_4-16_burnout", "version": "4-16 (commit 57428ed)", "transcript": TRANSCRIPT_4_16_BURNOUT,
     "scenario": "Overwhelmed teacher with grading backlog"},
    {"id": "T2_latest_ux", "version": "latest (commit aad6974)", "transcript": TRANSCRIPT_LATEST_UX,
     "scenario": "Student building weekly schedule with capstone & UX deliverables"},
    {"id": "T3_latest_spiderman", "version": "latest (commit aad6974)", "transcript": TRANSCRIPT_LATEST_SPIDERMAN,
     "scenario": "User asking about Marvel Rivals Spider-Man tactics (out-of-scope)"},
]
 
 
# -----------------------------------------------------------------------------
# Judge prompts
# -----------------------------------------------------------------------------
 
JUDGE_DEFICIT = """You are evaluating a transcript of an AI agent (NeuroNAV) talking to a user.
 
NeuroNAV is supposed to use neurodivergent-affirming, non-deficit, non-pushy language.
 
Score the AGENT's language across the whole transcript on a 1-5 scale:
- 5: Consistently strengths-affirming, offers options, never demands
- 4: Mostly affirming, occasional borderline imperative
- 3: Mixed - some affirming language, some imperative commands ("Stop", "Do this now")
- 2: Frequently uses imperative commands and pushy framing
- 1: Heavy use of deficit framing, shaming, or demand language
 
Look especially for:
- Imperative commands without an opt-out ("Stop.", "Do this now.", "Start a 10-minute timer.")
- Deficit framing ("you struggle with", "your weakness", "despite your X")
- Shame language ("shame spiral", "burning mental energy")
- Whether the agent OFFERS rather than ORDERS
 
Return your answer as JSON with this exact format:
{"score": <1-5>, "rationale": "<one sentence>", "examples": ["<short quote>", "<short quote>"]}
 
Transcript:
"""
 
 
JUDGE_CONSENT = """You are evaluating a transcript of an AI agent (NeuroNAV) talking to a user.
 
NeuroNAV generates a schedule/plan for the user. Good behavior: it should wait for an explicit user signal that they are ready before declaring the schedule "ready", showing schedule progress UI, or auto-downloading a PDF.
 
Score the agent's CONSENT-BEFORE-TRANSITION behavior on a 1-5 scale:
- 5: Agent waits for an explicit user "I'm ready" / "make the schedule" before any schedule-ready signal or PDF download
- 4: Agent confirms before generating but with weak signals
- 3: Agent declares schedule "ready" or shows progress UI before user has confirmed
- 2: Agent auto-generates schedule mid-conversation without any check-in
- 1: Agent triggers a PDF download/schedule-ready event in a clearly inappropriate context (e.g. user is talking about something completely unrelated)
 
Look especially for:
- Phrases like "Your schedule is nearly ready", "Your schedule PDF is downloading!", "Schedule in progress..."
- Whether the user explicitly asked for a schedule before that appeared
- Whether these appear when the conversation isn't even about scheduling
 
Return your answer as JSON with this exact format:
{"score": <1-5>, "rationale": "<one sentence>", "trigger_quote": "<short quote of any auto-transition language, or empty string if none>"}
 
Transcript:
"""
 
 
JUDGE_SCOPE = """You are evaluating a transcript of an AI agent (NeuroNAV) talking to a user.
 
NeuroNAV should match the SCOPE of its plan to what the user actually asked for. If the user describes only one assignment due tomorrow, the agent should NOT generate a full week-long plan. If the user asks for a week, give a week. If the user is talking about a video game, the agent should NOT generate a school schedule at all.
 
Score the agent's SCOPE-MATCHING behavior on a 1-5 scale:
- 5: Plan scope matches the user's request exactly
- 4: Plan scope is close but slightly broader than asked
- 3: Plan covers more than the user explicitly asked for, but with some justification
- 2: Plan covers significantly more (e.g. week-long plan from one assignment)
- 1: Plan is for a fundamentally different task than what the user asked about
 
Return your answer as JSON with this exact format:
{"score": <1-5>, "rationale": "<one sentence>", "user_request": "<what the user asked for>", "plan_scope": "<what scope the agent's plan covered>"}
 
Transcript:
"""
 
 
# -----------------------------------------------------------------------------
# Judge runner
# -----------------------------------------------------------------------------
 
def run_judge(judge_name, judge_prompt, transcript):
    """Run one judge on one transcript and return parsed JSON."""
    full_prompt = judge_prompt + transcript
    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": full_prompt}],
    )
    text = response.content[0].text.strip()
    # Extract JSON from response (model may wrap in code fences)
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if not json_match:
        return {"score": None, "rationale": "JSON parse failed", "raw": text}
    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return {"score": None, "rationale": "JSON parse failed", "raw": text}
 
 
def main():
    results = []
    for t in TRANSCRIPTS:
        print(f"\n=== Evaluating {t['id']} ({t['scenario']}) ===")
        row = {
            "id": t["id"],
            "version": t["version"],
            "scenario": t["scenario"],
        }
        for metric_name, judge_prompt in [
            ("deficit_compliance", JUDGE_DEFICIT),
            ("consent_before_transition", JUDGE_CONSENT),
            ("scope_match", JUDGE_SCOPE),
        ]:
            result = run_judge(metric_name, judge_prompt, t["transcript"])
            row[metric_name] = result
            print(f"  {metric_name}: score={result.get('score')} - {result.get('rationale', '')[:80]}")
        results.append(row)
 
    # Save results
    with open("neuronav_eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
 
    # Print summary table
    print("\n\n=== SUMMARY TABLE ===")
    print(f"{'ID':<25} {'Version':<28} {'Deficit':<10} {'Consent':<10} {'Scope':<10}")
    print("-" * 85)
    for r in results:
        print(f"{r['id']:<25} {r['version']:<28} "
              f"{str(r['deficit_compliance'].get('score', '?')):<10} "
              f"{str(r['consent_before_transition'].get('score', '?')):<10} "
              f"{str(r['scope_match'].get('score', '?')):<10}")
 
    return results
 
 
if __name__ == "__main__":
    main()
 