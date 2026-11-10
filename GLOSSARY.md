# Yocal Liturgics

Orthodox liturgical calendar and service-assembly for the Antiochian Archdiocese. Calendar calculation exists; service assembly (which hymns and variable texts go into which service) is being added.

## Language

**Divergence log**:
Hand-written record of accepted differences between generated output and an Answer key, each with a class (acceptable DCS difference or ANCA anomaly), a reason and a scope. A difference matching no entry is unexplained, and an unexplained ANCA difference blocks. UK divergences are not entered here.
_Avoid_: Diff log, exceptions

**Service**:
A single liturgical office on a given date (e.g. Sunday Divine Liturgy, Great Vespers on the eve).
_Avoid_: Office, event

**Variable part**:
A slot in a Service whose content depends on the date (e.g. apolytikion, kontakion, prokeimenon, epistle). Fixed text is not a Variable part.
_Avoid_: Proper, placeholder, variable (alone)

**Rule**:
A liturgical determination (e.g. "on a Sunday with a polyeleos saint, sing 6 resurrectional + 4 saint stichera") that selects or orders Variable parts. Every Rule cites its source.
_Avoid_: Algorithm, logic

**Inferred rule**:
A Rule with no explicit statement in any source, deduced from examples, and flagged as such alongside its evidence.
_Avoid_: Guess, assumption

**Answer key**:
An independent published service (Antiochian Archdiocese of North America service texts, then the GOA Digital Chant Stand) used to check generated output. A difference is a signal the Rules may be wrong, not proof.
_Avoid_: Reference, ground truth

**UK divergence**:
A deliberate difference between this project's output and the North American Answer key, arising from the existing UK calendar data (e.g. British saints). Expected, never logged and never treated as a Rule error. It is the difference between generating with and without UK-origin commemorations; only the output without them is compared with the Answer key.
_Avoid_: UK override, local variation

**Source**:
A published work a Rule is drawn from. Authority order: Antiochian Typikon, then Antiochian Archdiocese of North America, then Digital Chant Stand, then other Typika found.
_Avoid_: Reference, citation

**Major feast**:
Pascha, the Twelve Great Feasts (including the Circumcision/Basil's day) and the movable Paschal-cycle feasts (Palm Sunday, Ascension, Pentecost), in first-target scope with their preceding Vespers. The Triodion Sundays and Saturdays are in scope as Sunday-cycle days, not as Major feasts.
_Avoid_: Great feast (a narrower subset)

**Behavioural class**:
A small set of feast categories defined by the effect a commemoration has on a Sunday Service (Lord's feast replacing the Sunday, Theotokos feast sharing it, ordinary saint), not by a traditional rank. Nearest traditional ranks are noted where they line up.
_Avoid_: Rank, feast class

**Liturgical day**:
The unit of Service assembly: a calendar date together with its eve Vespers, so Saturday Great Vespers belongs to Sunday.
_Avoid_: Service day

**Slot**:
A named position in a Service that holds one or more Variable parts (e.g. the Lord, I Have Cried stichera in Vespers). Slot names follow Typikon terms. A Rule decides how many items fill a Slot and what they are.
_Avoid_: Position, section (alone)

**Hymn reference**:
A structured pointer to one hymn or text in a liturgical cycle (cycle, cycle coordinates such as tone and day, service-qualified kind, ordinal). A Rule emits it relative to the day (e.g. the tone of the week); the output carries it fully resolved. It identifies a Variable part without containing its text.
_Avoid_: Hymn id, key

**Principal commemoration**:
The one commemoration on a date whose properties decide the Service (e.g. whether the Vespers stichera have a glory). Chosen by a Rule; sources often do not state which it is._Avoid_: Lead commemoration, major commemoration, saint of the day (Typikon's term, narrower)


**Second commemoration**:
A commemoration other than the Principal commemoration that contributes its own set of Menaion stichera to a Sunday Service, so the Menaion portion is two sets of 3. Which date has one is mostly fixed by the date and inferred, not stated by any source.
_Avoid_: Secondary saint, alt commemoration (ALWB's term for a data block, not the liturgical notion)

**Great saint**:
A Typikon source term, left undefined by the Typikon; not a model term. Rules instead use two separate cited predicates: one for the Matins Sunday kontakion (the Typikon's explicit named list) and one for the saint's Epistle on a Sunday (the Typikon list plus saints ranked polyeleos or vigil by Bp Basil, inferred).
_Avoid_: Great saint in Rules or output

**Source conflict**:
An explicit Rule whose cited Source disagrees with the Answer key (ANCA). The Rule follows the higher-authority Source (Typikon) and carries the conflict's evidence. Status is `open` (unresolved, blocking), `accepted` (explained, e.g. as parish practice, non-blocking) or `misreading` (no real disagreement). Distinct from a Divergence log entry (known anomaly of the key) and a UK divergence (deliberate).
_Avoid_: Rule error, mismatch
