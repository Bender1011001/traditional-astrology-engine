# Jaimini extraction notes

Status: research working notes for `jaimini_upadesa_sutra_v1`
Date: 2026-08-02
Translation grade for every rendering below: **`engine_translation_unreviewed`**

## How to read this file

Every sūtra below is given in three layers, in this order:

1. **OCR verbatim** — the raw Devanagari exactly as it came out of the
   archive.org text layer for `in.ernet.dli.2015.242319`, including its errors.
   This is what was actually retrieved.
2. **Restored reading** — the Sanskrit as I read it, with OCR damage repaired.
   Repairs are constrained by the commentary, which glosses each sūtra word by
   word, and by Abhyankar's independent English. Every restoration is a
   judgement and is marked where it is more than mechanical.
3. **Rendering** — my English. Unreviewed. Where Abhyankar's 1951 English
   differs in substance, both are given.

The point of showing layer 1 is that a specialist can check layers 2 and 3
against it without trusting me. Where the OCR will not support a restoration, I
say so rather than smoothing it.

Numbering note, and it matters: **the two witnesses diverge by one from 1.1.15
onward.** Sūtrārthaprakāśikā numbers are given first, Abhyankar's in brackets.
The cause is documented in §3 below.

---

## 1. The aspect sūtras — Jaimini's first point of departure

### 1.1.2 [Abh 1.1.2] — rāśi dṛṣṭi

- **OCR verbatim:** `अभिपदयन्तयक्षाणि पार््चसेच॥२॥`
- **Restored:** `अभिपश्यन्त्यृक्षाणि पार्श्वे च ॥२॥`
  *abhipaśyanty ṛkṣāṇi pārśve ca*
  The OCR mangles `पश्य`→`पदय`, `ऋक्षाणि`→`यक्षाणि` and collapses `पार्श्वे च`
  into `पार््चसेच`. The commentary's own gloss (`पार्श्वे इति सप्तम्या
  एकवचनं`, "*pārśve* is a locative singular, not an accusative dual") fixes the
  form and is why the restoration is safe.
- **Rendering:** "The signs aspect [those] in front, and at the side."
- **Abhyankar:** "The (twelve) Divisions aspect the Divisions in their front;
  so also they aspect the Divisions at the two sides."

The sūtra alone would not tell you which signs. The commentary supplies a
vṛddha kārikā that does:

- **OCR verbatim:** `““चरं धनं विना स्थाप्णुः स्थिरमन्त्यं विना चरम्‌" ।
  युग्मं स्वेन व्रिना युग्मं पद्यतीत्ययमागमः ॥`
- **Restored:** `चरं धनं विना स्थाणुः स्थिरमन्त्यं विना चरम् । युग्मं स्वेन
  विना युग्मं पश्यतीत्ययमागमः ॥`
- **Rendering:** "A fixed sign [aspects] the movable, except the second; a
  movable sign the fixed, except the twelfth; a dual sign aspects the dual,
  except itself. This is the tradition."

Worked out, that gives movable → 5th, 8th, 11th; fixed → 3rd, 6th, 9th; dual →
4th, 7th, 10th — and the commentary states exactly those triads independently a
few lines later, which is a genuine internal cross-check rather than my
arithmetic. Encoded as `jaimini.rasi-drsti.movable` / `.fixed` / `.dual`.

**This is the tradition's signature.** Parāśari aspect is a property of grahas;
Jaimini aspect is a property of signs, and grahas only inherit it.

### 1.1.3 [Abh 1.1.3] — grahas inherit

- **OCR verbatim:** `तन्निषटाश्च तदत्‌ ॥ ३ ॥`
- **Restored:** `तन्निष्ठाश्च तद्वत् ॥३॥` — *tanniṣṭhāś ca tadvat*
- **Rendering:** "And those established in them, likewise."

---

## 2. The argalā sūtras, and the kaṭapayādi problem

The argalā sūtras are written in numeric code. Encoded as
`jaimini.katapayadi.bhava-and-rasi`, and this is why nearly every dispute in
this text is at bottom a decoding dispute.

### 1.1.4 [Abh 1.1.4]

- **OCR verbatim:** `द्‌रभाग्यशरस्या ऽ्गला निध्यातः ॥ ४ ॥`
- **Restored:** `दारभाग्यशूलस्था अर्गला निध्यातुः ॥४॥`
  *dārabhāgyaśūlasthā argalā nidhyātuḥ*
- **Rendering:** "[Grahas] standing in *dāra*, *bhāgya*, *śūla* are an argalā
  from the observer."

The commentary decodes it and shows its working, which is the single most
useful passage in the whole witness:

> `दकारस्याष्टसंख्या रेकारस्य द्विसंख्या अष्टाविंशतिमिते द्वादशतष्टे शेषं
> चतुर्मितम्`
> "*da* has the value 8, *ra* the value 2 → 28; divided by twelve, the
> remainder is 4."

So *dāra* = the 4th house. Likewise *bhāgya* = 2nd and *śūla* = 11th, which the
commentary states outright (`तुर्यद्वितीयैकादशस्थानस्थिता`). Abhyankar's
English independently gives "fourth, second and eleventh." Two witnesses, same
answer, from completely different directions.

The same machinery decodes *kāma* = 3 (1.1.5), *riṣpha* = 12 and *nīca* = 10
(1.1.6), and *viveka* = 144 (1.1.33).

### 1.1.5 — 1.1.9

| Sūtra | OCR verbatim | Restored | Rendering |
|---|---|---|---|
| 1.1.5 | `कामस्था तु भृयसा पापानाम्‌ ॥ ५॥` | कामस्था तु भूयसा पापानाम् | "But [an argalā] standing in *kāma* [the 3rd] is by the many, of malefics." |
| 1.1.6 | `रिष्फनीचकासस्था विरोधिनः ॥ ६ ॥` | रिष्फनीचकामस्था विरोधिनः | "Those standing in *riṣpha*, *nīca*, *kāma* are obstructors." |
| 1.1.7 | `न न्यूना विवलाश्च ॥ ७ ॥` | न न्यूना विबलाश्च | "Not [those] fewer, nor the weak." |
| 1.1.8 | `भाग्वत्‌ त्रिकोणे ॥ ८ ॥` | प्राग्वत् त्रिकोणे | "As before, in the trine." |
| 1.1.9 | `विपरोतं केतोः ॥ ९ ॥` | विपरीतं केतोः | "Reversed, for Ketu." |

The 1.1.8 restoration `भाग्वत्` → `प्राग्वत्` is a repair of a common
Devanagari OCR confusion (`प्रा` read as `भा`) and is confirmed by the
commentary's own repeated use of `प्राग्वत्` in its gloss and by Abhyankar's
"Similar combination takes place."

---

## 3. The chara kārakas — the high-value block

This is the part of the tradition that is directly implementable, and the part
where the witnesses disagree most consequentially.

### 1.1.10 [Abh 1.1.10] — the Ātmakāraka

- **OCR verbatim:** `आत्माधिकः कटादिभि्नभोगः सप्तानामष्टानां वा ॥ १०॥`
- **Restored:** `आत्माधिकः कलादिभिर्नभोगः सप्तानामष्टानां वा ॥१०॥`
  *ātmādhikaḥ kalādibhir nabhogaḥ saptānām aṣṭānāṃ vā*
  `कटादिभिः` → `कलादिभिः` is required by the commentary, which glosses the word
  as measurement in *kalā*s (minutes) and says so twice.
- **Rendering:** "The Ātmā is the sky-goer [graha] greatest by minutes and so
  on, of the seven or of the eight."
- **Abhyankar:** "That planet (out of the seven or eight planets) who is more
  ahead than others (in degrees and minutes ...) is called the Chief
  Significator."

Commentary, on what "greatest" measures:

> `यत्र ग्रहाणां ग्रहयोर्वा मध्ये अंशतुल्यता चेत् तदा कलादिस्थानेन योऽधिकः स
> आत्मकारको भवति`
> "If among the grahas, or between two of them, there is equality of degrees,
> then whichever is greater by minutes and so on becomes the Ātmakāraka."

And the vṛddha verse giving the full ranking:

- **OCR verbatim:** `“भभागाधिकः कारकः स्यादल्पभागोऽन्त्यकारकः । मध्यांशो
  मध्यखेटः स्यादुपखेट; स पव हि" ॥`
- **Restored:** `भागाधिकः कारकः स्यादल्पभागोऽन्त्यकारकः । मध्यांशो मध्यखेटः
  स्यादुपखेटः स एव हि ॥`
- **Rendering:** "The one greatest in degrees is the kāraka; the one least in
  degrees is the last kāraka; the middle-degree one is the middle planet, and
  that same one is the *upakheṭa*."

**Answering the question directly: yes, the assignment rule is precisely
stateable from the sūtras.**

> Compute each graha's sidereal longitude modulo 30 — its degrees within its
> occupied sign. Sort descending. The highest is the Ātmakāraka, and each
> successive rank takes the next kāraka title. On equality of degrees, compare
> minutes, then finer units.

That is arithmetic, it is testable, and it is encoded as
`jaimini.chara-karaka.atmakaraka.by-degree` with vector
`jaimini.v.karaka.rank.seven`. **What is not settled is the candidate set**, and
that changes the answer — see §3.2 and §3.3.

### 3.1 The kāraka chain

- **OCR verbatim:** `तस्यानुसरणादमालयः ॥ १२ ॥ तस्य श्रता ॥ १३ ॥ तस्य माता ॥ १४
  ॥ तस्य पुत्रः ॥ १५ ॥ तस्य ज्ञातिः॥१६॥ तस्य दाराश्च ॥ १.७ ॥`
- **Restored:** `तस्यानुसरणादमात्यः ॥१२॥ तस्य भ्राता ॥१३॥ तस्य माता ॥१४॥ तस्य
  पुत्रः ॥१५॥ तस्य ज्ञातिः ॥१६॥ तस्य दाराश्च ॥१७॥`
- **Rendering:** "By following after him, the Minister. His brother. His
  mother. His son. His kinsman. And his wife."

Note what is **not** there: no `तस्य पिता`. The Sūtrārthaprakāśikā's running
text has **seven** kārakas.

### 3.2 DISAGREEMENT — seven kārakas or eight

Abhyankar's critical text, edited from fifteen manuscripts, **does** have a
Pitṛkāraka sūtra:

> Abh 1.1.15: "The planet next to the Significator of the Mother is called the
> Significator of the Father (Pitṛkāraka)."

That one sūtra is the entire cause of the numbering divergence between the
witnesses from 1.1.15 onward.

The Sūtrārthaprakāśikā knows about those manuscripts and rejects them:

> `क्वचित् पुस्तकेषु मातृकारकान्न्यूनांशः पितृकारको भवतीति श्रुतं तदसङ्गतम् ।
> आदौ मातृकारकनिरूपणस्यायोग्यत्वात्`
> "In some books it is heard that 'the one of fewer degrees than the Mātṛkāraka
> is the Pitṛkāraka' — that is incoherent, since it is inappropriate for the
> Mātṛkāraka to be defined first."

And the sūtra it prints instead:

- **OCR verbatim:** `मात्रा सह पुत्रमेकं समामनन्ति ॥ १८ ॥`
- **Rendering:** "Some hold the son together with the mother."
- **Abhyankar** [1.1.19]: "Some scholars maintain the tradition of taking the
  Significator of the mother as the Significator of the son also, (taking the
  number of significatory planets as seven and not eight, of course omitting
  Rahu)."

Both witnesses therefore report **both** schemes; they differ on which is the
main text and which is the reported variant. The sūtra itself refuses to
choose — `सप्तानामष्टानां वा`, "of seven or of eight." Encoded as
`jaimini.chara-karaka.scheme.seven` and `.eight`, marked `conflicts_with` each
other.

Unresolved and flagged: under the seven-kāraka reading, collapsing Mātṛ and
Putra leaves six titles for seven ranked bodies. Vector
`jaimini.v.karaka.rank.seven` records my reading of the mapping and flags it as
needing a specialist.

### 3.3 DISAGREEMENT — Rāhu, and whether it is reverse-counted

This is the other half of the candidate-set problem, and the commentary states
it in one verse:

- **OCR verbatim:** `^“मेषाद्यसव्यमार्गेण रोटुकेत्‌ न कारक" ।`
- **Restored:** `मेषाद्यसव्यमार्गेण राहुकेतू न कारकौ`
- **Rendering:** "By the *asavya* path from Aries onward, Rāhu and Ketu are not
  kārakas."

The commentary's gloss is what makes it usable:

> `सव्यं वाममसव्यं दक्षिणं तेन मेषादिक्रममार्गेण राहुकेतू कारकौ न भवतः ।
> विपरीतमार्गेण तु भवत एव ।`
> "*savya* is left, *asavya* is right; therefore by the Aries-order path Rāhu
> and Ketu are not kārakas — but by the reverse path they certainly are."

And immediately after:

> `राहोर्न्यूनांशत्वेनात्मकारकत्वं स्यादिति वृद्धेनापि प्रतिपादितम्`
> "That Rāhu, by having fewer degrees, may become the Ātmakāraka — this too has
> been propounded by the ancient [authority]."

Read together, these say: measure Rāhu backwards, i.e. at 30° − λ. A Rāhu early
in a sign then ranks *high*, which is exactly what "by having fewer degrees it
becomes Ātmakāraka" describes. Encoded as
`jaimini.chara-karaka.rahu.reverse-counted`, with the flat-exclusion reading as
`jaimini.chara-karaka.rahu.excluded`.

Abhyankar adds a third datum from a different direction: Rāhu and Ketu "possess
the same number of degrees in a Rasi" and so "are considered together as one
Karaka Graha" — which is how eight kārakas rather than nine are obtained.

**Why this matters practically.** Vectors `jaimini.v.karaka.rank.seven` and
`jaimini.v.karaka.rank.eight-with-rahu-reversed` use the *same* set of planetary
longitudes. Under seven kārakas the Ātmakāraka is the Sun; under eight with
reversal it is Rāhu. Same chart, different soul-significator, different reading.
No engine may pick between these silently.

### 3.4 DISAGREEMENT — the tie-break

Three positions in one passage, each attributed:

- the sūtra's own `कलादिभिः` — go to minutes and finer;
- `के चित् तु ... यो बली स आत्मा` — "but *some* say the stronger is the Ātmā",
  of which the commentator says `तत्र मूलमन्वेष्यम्`, "the source for that
  should be sought";
- the commentator's own: `अस्मन्मते तु अंशसाम्ये यो बली स आत्मा`;
- the **Subodhinī**'s, quoted at length and dismissed as `तदसङ्गतम्`.

Encoded as `jaimini.chara-karaka.tie-break.disputed`; the engine abstains.

### 3.5 The Parāśari cross-reference, quoted by the commentary itself

The Sūtrārthaprakāśikā quotes a Bṛhat-Pārāśara-Horā-Sārāṃśa passage in full at
1.1.10, including:

> `रव्यादिशनिपर्यन्ता भवेयुः सप्त कारकाः । अंशसाम्ये ग्रहौ द्वौ चेद्राहुं तान्
> गणयेद् द्विज ॥`
> "From the Sun through Saturn there are seven kārakas. If two grahas are equal
> in degrees, O twice-born, count Rāhu among them."

So the seven/eight fork is not a Jaimini-versus-Parāśara split. It runs *inside*
both corpora, and the Jaimini commentator reaches for Parāśara as a witness on
his own side.

---

## 4. Sthira kārakas — a second, fixed layer

Jaimini runs variable and fixed significators **simultaneously**. Abhyankar's
term for the chara set is *anitya* (impermanent) kārakas as against the *nitya*
(permanent) ones of 1.1.19–1.1.23.

| Sūtra | OCR verbatim | Rendering |
|---|---|---|
| 1.1.19 [Abh 1.1.20] | `भगिन्यारतः इयाः कनीयान्‌ जननी च ॥ १९ ॥` | "Sister, brother-in-law, younger brother and mother — from *ārta* [Mars]." |
| 1.1.20 [Abh 1.1.21] | `मातुलाद्यो वन्धवो मातृसजातीया इव्यत्तरतः ॥ २० ॥` | "Maternal uncle and other kin, and the mother's kindred — thus, from the next [Mercury]." |
| 1.1.21 [Abh 1.1.22] | `पितामहः पतिपुत्राविति गुरुमुखादेव जानीयात्‌ ॥ २१ ॥` | see below |

### DISAGREEMENT — 1.1.21 [Abh 1.1.22]

The sūtra says `गुरुमुखादेव` — "from Jupiter onward" or "from Jupiter's mouth",
i.e. from Jupiter itself.

- **Abhyankar:** "Grandfather, husband and son should be considered from
  Jupiter." All three from one graha.
- **Sūtrārthaprakāśikā:** `गुरोः पितामहः शुक्रात् पतिः शनेः पुत्र इति
  जानीयात्` — "grandfather from Jupiter, husband from Venus, son from Saturn."
  Three topics, three grahas, taking *gurumukhāt* as "beginning from Jupiter."

Encoded as `jaimini.sthira-karaka.jupiter-venus-saturn.disputed`.

---

## 5. Daśā counting — where the witnesses agree

| Sūtra | OCR verbatim | Rendering |
|---|---|---|
| 1.1.24 [Abh 1.1.25] | `परानीक्ततिर्वि षमभेष ॥ २४ ॥` → `प्राचीवृत्तिर्विषमभेषु` | "Eastward [forward] motion in odd signs." |
| 1.1.25 [Abh 1.1.26] | `पराड्लयोत्तरषु ॥ २५ ॥` → `पराच्युत्तरेषु` | "Westward [reverse] in the others." |
| 1.1.26 [Abh 1.1.27] | `नक्र चित्‌ ॥ २६॥` → `न क्वचित्` | "Not in some cases." |

The exception is stated by the sage himself, quoted in the commentary:

> `मातृधर्मयोः सामान्यं विपरीतमोजकूटयोः`

decoded by the commentary to Leo and Aquarius (the 5th and 11th) plus Taurus
and Scorpio (*ojakūṭa*), and confirmed by an old kārikā:

> `क्रमाद् वृषे वृश्चिके च व्युत्क्रमात् कुम्भसिंहयोः`
> "Forward in Taurus and Scorpio; reversed in Aquarius and Leo."

Abhyankar's English independently gives the exception as "divisions 2, 5, 8 and
11" — the same four signs. **The witnesses agree.** Worth stating plainly,
because this file otherwise reads like a catalogue of disputes.

The commentary also preserves **Nīlakaṇṭha's own summary verse** on these three
sūtras — one of only two places where his words survive in the retrieved
material:

- **OCR verbatim:** `“ेपादिभिचिमेकगेयं पदमोजपदे क्रमात् । दशाब्दानयने कार्या
  गणना व्युःकमःत् समे” ॥`
- **Partially restored:** `मेषादिभिः ... पदमोजपदे क्रमात् । दशाब्दानयने कार्या
  गणना व्युत्क्रमात् समे ॥`
- **Rendering:** "... from Aries onward ... the pada in an odd sign, in order;
  in deriving the daśā years the counting is to be done in reverse for an even
  [sign]."
- The second half is secure; the first half is too damaged to restore and is
  left broken rather than guessed.

---

## 6. Special lagnas — rates settled, origin disputed

The rates come from a vṛddha verse:

- **OCR verbatim:** `“सूर्योदयं समारभ्य घरिकानां तु पञ्चकम्‌ । प्रयाति
  जन्मपर्यन्तं भावलग्नं तथेव च ॥ तथा साधंदिघटिज्ानितात्‌ कालाह्धिटग्नभान्‌ ।
  प्रयाति ग्नं तन्नाम ह।रालग्नं प्रचक्षते" ॥`
- **Restored:** `सूर्योदयं समारभ्य घटिकानां तु पञ्चकम् । प्रयाति जन्मपर्यन्तं
  भावलग्नं तथैव च ॥ तथा सार्धद्विघटिकामितात् कालाद्विलग्नभात् । प्रयाति लग्नं
  तन्नाम होरालग्नं प्रचक्षते ॥`
- **Rendering:** "Beginning from sunrise, [one sign per] five ghaṭikās proceeds
  up to birth — that is the Bhāva Lagna. Likewise from a time measured in two
  and a half ghaṭikās the sign proceeds; that they call the Horā Lagna."

Bhāva Lagna: one sign per 5 ghaṭikās (2 hours). Horā Lagna: one sign per 2.5
ghaṭikās (1 hour). Ghaṭikā Lagna, from the commentary's prose only: one sign per
ghaṭikā (24 minutes).

### DISAGREEMENT — where the count starts, and Nīlakaṇṭha's second appearance

> `जन्मलग्ने विषमे सूर्यराशितः समे जन्मलग्नाद्धोरालग्नं भावलग्नं च गणनीयमिति
> प्राचीनाः । अयमेवाभिप्रायो वृद्धेनापि प्रतिपादितः परन्तु नीलकण्ठेनोक्तम्
> "कारिकातोऽयमर्थो नायाति" इति सम्यग्विरुद्धम् । यतो या पूर्वकारिका सा तु
> श्रीमता नीलकण्ठेन त्यक्ता ।`

"The ancients say: when the birth lagna is odd, the Horā and Bhāva Lagnas are to
be counted from the Sun's sign; when even, from the birth lagna. This same
intent was propounded by the *vṛddha* as well. **But Nīlakaṇṭha said, 'this
sense does not follow from the kārikā'** — which is entirely wrong, since the
earlier kārikā was simply discarded by the honourable Nīlakaṇṭha."

The commentator's own position, and his unusual candour about it:

> `अस्माकमेव मतम् । भावलग्नं होरालग्नं घटिकालग्नं च सूर्यादेव गणनीयम् । यतः
> सर्वेषामेव लग्नानां सूर्यादेव प्रवृत्तिः ।`
> "Our own view: the Bhāva, Horā and Ghaṭikā Lagnas are all to be counted from
> the Sun, since all the lagnas begin from the Sun."

> `अत्र मन्मतमेव मुख्यमिति नास्माकमाग्रहः । केवलं सद्युक्तिरेव मया प्रदर्शिता ।`
> "I do not insist that my own view is the principal one; I have only set out a
> sound argument."

Three positions, one of which — Nīlakaṇṭha's — survives here **only as a
negation reported by an opponent**. We know what he denied; we do not know what
he affirmed. Encoded as `jaimini.special-lagna.origin.disputed`. Recovering his
positive rule requires the Jammu manuscript, which is why that transcription is
the top item on the missing-work list.

### Varṇada, and an honest admission

- **OCR verbatim (opening):** `^“ओजयप्नभ सूतानां मेषादेर्गणयेत्‌ कमात्‌ ।
  युग्मलघ्चप्रसूतानां मीनदेरपसव्यतः ॥`
- **Restored:** `ओजलग्नप्रसूतानां मेषादेर्गणयेत् क्रमात् । युग्मलग्नप्रसूतानां
  मीनादेरपसव्यतः ॥ ... मेषमीनादितः पश्चाद्यो राशिः स तु वर्णदः ।`
- **Rendering:** "For those born in an odd lagna, count forward from Aries; for
  those born in an even lagna, backward from Pisces. Count from Aries or Pisces
  to the birth lagna, and likewise to the Horā Lagna. If both are of the same
  kind — masculine or feminine — add them; if of different kinds, subtract. The
  sign thereafter from Aries or Pisces is the Varṇada."

Twice in this passage the commentator says he does not understand his own
source:

> `परन्तु आचार्येण कथमेवं तमिति न विद्मः` — "But why the teacher said it thus,
> we do not know."
> `परन्तु आचार्येण कथमोजलग्नेत्यादिकृतं तन्न विद्मः` — "But why the teacher
> framed it as 'odd lagna' and so forth, we do not know."

He also notes that in his own worked examples, simply adding the two lagna
longitudes as they stand reaches the same Varṇada. Encoded as
`jaimini.special-lagna.varnada.computation` and
`.varnada.commentator-uncertainty`. The engine may compute Varṇada and display
it; it may not delineate it as settled.

---

## 7. Two more sūtras worth recording

**1.1.23 [Abh 1.1.24]** — `मन्दोऽज्यायान्‌ ग्रहेषु ॥ २३ ॥` — "Saturn is the
least among the grahas." The full ascending order (Saturn, Mars, Mercury,
Jupiter, Venus, Moon, Sun) is **not** in the sūtra; the commentary imports it
from Varāhamihira's Bṛhajjātaka and says so. That same series is already encoded
on the Parāśari side of this repo, so it is a real point of agreement between
the branches — recorded as such rather than presented as a Jaimini discovery.

**Abh 1.1.35** — `होरादयः सिद्धाः`, "Horā and the rest are established [i.e.
take them as current]." Jaimini **declines to define his own vargas**. Any
divisional chart a Jaimini engine uses is imported, and must be attributed to
the text it was imported from. Encoded as a delegation, and listed as a
`refused` row in the defensibility spec.

---

## 8. Every commentator disagreement found, in one place

| # | Locus | Parties | What is at stake |
|---|---|---|---|
| 1 | 1.1.4 | Sūtrārthaprakāśikā vs **Subodhinī** | Does argalā act on the bhāva under consideration or on the aspecting graha? |
| 2 | 1.1.4 | Sūtrārthaprakāśikā vs **Nīlakaṇṭha** | Nīlakaṇṭha explains a sandhi as Vedic (*chāndasa*); the commentator calls this `असमीचीनम्`, "not correct", and argues *argalā* is simply attested in both genders |
| 3 | 1.1.5 | Sūtrārthaprakāśikā vs **Premanidhi Paṇḍita** | Does *bhūyasā* count malefic bodies (3+) or select the malefic with the greatest arc? Called `असङ्गतम्` |
| 4 | 1.1.5 | Sūtrārthaprakāśikā vs Abhyankar | Three-or-more malefics, or malefics outnumbering benefics? These differ whenever two malefics sit alone |
| 5 | 1.1.2 | Sūtrārthaprakāśikā vs the Kārikā / Subodhinī | Which aspected sign is *sammukha*; and whether a square or circular chart figure governs |
| 6 | 1.1.9 | Sūtrārthaprakāśikā vs `कैश्चित्` | Does *viparītaṃ ketoḥ* reverse every preceding argalā sūtra, or only the trine sūtra it follows? |
| 7 | 1.1.10 | Sūtrārthaprakāśikā vs `के चित्` vs **Subodhinī** | How to break a kāraka tie |
| 8 | 1.1.10 / 1.1.18 | **Abhyankar's 15 MSS** vs Sūtrārthaprakāśikā's text | Seven kārakas or eight; whether a Pitṛkāraka sūtra is authentic. Causes the numbering divergence |
| 9 | 1.1.10 | vṛddha verse, both directions | Rāhu excluded, or included and reverse-counted |
| 10 | 1.1.21 | Abhyankar vs Sūtrārthaprakāśikā | Grandfather, husband, son all from Jupiter — or split across Jupiter, Venus, Saturn |
| 11 | 1.1.31 | **Nīlakaṇṭha** vs *prācīnāḥ* vs Sūtrārthaprakāśikā | Where the Horā and Bhāva Lagna counts begin |
| 12 | 1.1.31 | the commentator vs himself | Varṇada: he transmits the rule and twice says he cannot explain it |

Ten of the twelve are encoded as separate attributed rules. Numbers 2 and 5 are
recorded here but not promoted: number 2 is a grammatical dispute with no
computational consequence, and number 5 rests on an OCR passage whose referent I
could not determine.

---

## 9. Missing work

Ordered by leverage, not by convenience.

1. **Page images for `jaimini-kva-a-4-size`** (238 MB). Its OCR recovered
   English and *zero* Devanagari. Behind it sit: Abhyankar's critical apparatus
   from fifteen manuscripts — the only thing that can settle the Pitṛkāraka
   question — his Appendix 1 (the Jaimini-Sūtra-Kārikā, source of several verses
   this pack currently receives only at second hand), his Appendix 4
   (comparative contents against Bṛhad-Yavana-Jātaka, Bṛhajjātaka, Sārāvalī and
   Bṛhat Pārāśarī), and fourteen worked kāraka-kuṇḍalīs of named modern figures.
   One acquisition, four blockers cleared.
2. **Devanagari transcription of the Jammu Nīlakaṇṭha manuscript**, folios
   covering Adhyāya 1 Pāda 1. At present the tradition's most-cited commentator
   reaches us only through the words of a man arguing against him. That is not
   an acceptable basis for attributing positions to him.
3. **Independent Sanskrit review** of every restoration in this file. A single
   unreviewed reading is a single point of failure for every rule built on it,
   and several restorations here (`कलादिभिः`, `प्राग्वत्`, `अभिपश्यन्ति`) carry
   real doctrinal weight.
4. **Adhyāya 1 Pādas 2–4, and Adhyāyas 2–4.** Nothing outside 1.1 has been read
   in the original. Missing: upapada, the yogas, Chara/Sthira/Nārāyaṇa daśā
   construction, daśā period arithmetic, the Brahmā/Maheśvara/Rudra grahas, and
   the whole āyurdāya apparatus.
5. **Confirm the Sūtrārthaprakāśikā's authorship and date** from its title page.
   It is currently the primary Sanskrit witness for this pack and its author is
   identified only by an Archive record.
6. **Sūtra-numbering concordance** across all witnesses, including Rao. Until
   that exists, every external citation of "Jaimini 1.1.15" is ambiguous.
7. **Ārūḍha Sanskrit.** Rules 1.1.29–1.1.31 are encoded from Abhyankar's English
   alone, and the inclusive-counting convention is assumed rather than sourced.
8. **A clean OCR or scan of Suryanarain Rao's translation.** The retrieved copy
   is unreadable — a Devanagari OCR profile applied to an English book.
