# Reading Generation Strategy Testing

## Overview
This directory contains an experimental script to test different strategies for generating comprehensive 20-page astrological readings using LLMs.

## Problem Statement
We want to generate ~20-page comprehensive astrological readings that:
1. Include everything we can tell someone about their chart
2. Make predictions about past and future events
3. **MUST FOLLOW THE RULES** - only use data from the chart and Binder1 reference material
4. **NEVER MAKE ANYTHING UP** - no fabricated aspects, positions, or interpretations

## Strategies Being Tested

### Strategy 1: Single Comprehensive Prompt
**Approach:** Send one large prompt asking for everything at once (8,000+ words)

**Pros:**
- Simple and fast
- One API call
- Coherent narrative from start to finish

**Cons:**
- May hit token limits
- LLM may compress content to fit limits
- Less depth on individual topics

### Strategy 2: Iterative "What Else" Prompting
**Approach:** Start with base reading, then ask "what else can you tell me" 6 times in a row

**Pros:**
- Can accumulate substantial detail
- LLM maintains context across iterations
- Natural expansion of topics
- Can reach higher word counts

**Cons:**
- Takes longer (6 API calls)
- May repeat some information
- Requires careful prompting to avoid redundancy

### Strategy 3: Structured Section-by-Section
**Approach:** Request specific sections one at a time, then synthesize into final document

**Pros:**
- Maximum control over depth per section
- Can ensure all topics are covered
- Very focused analysis

**Cons:**
- Takes longest (7+ API calls)
- Needs careful synthesis step
- May be less natural/flowing

## Usage

### Basic Test (All Strategies)
```bash
python src/scripts/test_reading_strategies.py \
  --name "John Doe" \
  --date "1996-08-13" \
  --time "07:18" \
  --city "Fairfield" \
  --state "California"
```

### Test Single Strategy
```bash
# Strategy 1 only
python src/scripts/test_reading_strategies.py \
  --name "Jane Smith" \
  --date "1990-08-26" \
  --time "16:20" \
  --city "Vacaville" \
  --state "California" \
  --strategy 1

# Strategy 2 only (with custom iterations)
python src/scripts/test_reading_strategies.py \
  --name "Jane Smith" \
  --date "1990-08-26" \
  --time "16:20" \
  --city "Vacaville" \
  --state "California" \
  --strategy 2 \
  --iterations 8

# Strategy 3 only
python src/scripts/test_reading_strategies.py \
  --name "Jane Smith" \
  --date "1990-08-26" \
  --time "16:20" \
  --city "Vacaville" \
  --state "California" \
  --strategy 3
```

### Custom Output Directory
```bash
python src/scripts/test_reading_strategies.py \
  --name "Test User" \
  --date "1996-08-13" \
  --time "07:18" \
  --city "Fairfield" \
  --state "California" \
  --output-dir "my_test_results"
```

## Output

The script creates markdown files in the output directory with naming format:
- `{name}_strategy1_{timestamp}.md` - Single comprehensive prompt result
- `{name}_strategy2_{timestamp}.md` - Iterative "what else" result  
- `{name}_strategy3_{timestamp}.md` - Structured section result

Each file contains:
- Strategy description
- Full reading output
- Metadata (word count, estimated pages)

## Evaluation Criteria

When comparing results, evaluate on:

1. **Length**: Did we reach ~20 pages (8,000+ words)?
2. **Accuracy**: Are all statements grounded in the chart data?
3. **Comprehensiveness**: Are all major topics covered?
4. **Predictions**: Are past/future predictions based on timing techniques?
5. **Readability**: Is the narrative flowing and engaging?
6. **No Fabrication**: Zero made-up information?

## Current Implementation in Production

The current production implementation in `chat_oracle.py` uses a hybrid approach for paid tier:
- Multiple focused prompts (6 turns)
- Each turn builds on previous
- Final synthesis combines all parts
- Aiming for 5,000+ words

This experimental framework allows us to test if alternatives might work better.

## Next Steps

1. Run tests with sample chart data
2. Compare outputs across strategies
3. Measure word counts, quality, adherence to rules
4. Select the best approach
5. Update production implementation if needed

## Requirements

- OpenRouter API key set in environment (`OPENROUTER_API_KEY`)
- Access to Gemini 3 Pro or equivalent model
- Binder1.txt reference material in project root
