# Attack class taxonomy

Fifteen classes are defined for v1.0. The enum in `data/schema.json` is frozen at
these values; adding, renaming or removing a class is a schema change, not an
editorial one.

## Rules that apply to every class

1. **Exactly one class per entry.** An entry that plausibly fits two classes is
   filed under one of them. The entry's `impact` or `summary` states that a second
   class was considered and names the tie-break rule that decided the call.
2. **Tie-break rules must be decidable from the entry's own facts.** A tie-break
   that needs taste is not a tie-break. Each class below has a rule keyed on a
   property the source text states: which channel carried the payload, which
   component failed, which artefact moved, or which step yielded capability.
3. **The recurring pattern** across the tie-break rules below: when an attack has
   both a mechanism and an outcome, classify by the step that *yielded attacker
   capability*, not by the step that produced the visible outcome.
4. **A class is not a severity ranking.** The classes describe mechanisms. The
   evidence tier in `docs/TIERS.md` describes how well the attack is established.
   The two axes are independent.

---

## PROMPT_INJECTION_DIRECT

- **Definition:** instructions typed or sent by a human or an operator into the
  model context, intended to redirect the model away from its assigned task.
- **Inclusion test:** Does the injected text enter the model's context through the
  normal user or operator input channel?
- **Tie-break rule:** If the success of the injection is that the model emits
  content it would otherwise refuse, the entry is JAILBREAK; if the success is
  that the model performs a task or takes an action it would otherwise not take,
  it is PROMPT_INJECTION_DIRECT. The rule keys on what the source states was
  obtained, not on the wording of the injection.
- **Most confused with:** JAILBREAK (see the tie-break rule above).

## PROMPT_INJECTION_INDIRECT

- **Definition:** attacker-authored instructions embedded in content the system
  retrieves and places in the model context, where the model treats them as
  commands.
- **Inclusion test:** Does the payload travel through retrieved content the system
  fetched on its own initiative, such as a web page, a document, a search result,
  or an issue comment the agent was asked to summarise?
- **Tie-break rule:** Key on who owns the delivery channel. If the payload arrived
  in a tool schema, tool description or server-supplied metadata, the entry is
  TOOL_POISONING. If it arrived in ordinary retrieved content that any publisher
  could write, the entry is PROMPT_INJECTION_INDIRECT. A page the attacker also
  controls is still ordinary retrieved content unless the page *is* the tool
  definition or the tool's documentation as consumed by the agent.
- **Most confused with:** TOOL_POISONING, which is the same delivery into the same
  context but through a channel the tool operator controls.

## TOOL_POISONING

- **Definition:** a malicious or misleading payload delivered through a tool or
  function definition that an agent reads before deciding what to do, including
  MCP server tool descriptions, server instructions and tool metadata.
- **Inclusion test:** Does the payload sit in a schema, description, metadata field
  or server-instruction block that the tool or MCP server operator controls and
  publishes as part of the tool's definition?
- **Tie-break rule:** Key on the step that yielded capability. If the tool
  definition alone caused the agent to select the tool, misdescribe its arguments
  or take an unintended action, the entry is TOOL_POISONING, even when the
  resulting act exfiltrated data. If the tool behaved as documented and the damage
  came from what the tool returned, the entry is PROMPT_INJECTION_INDIRECT. If the
  tool behaved as documented and the damage came from the application's use of the
  tool's output, the entry is INSECURE_OUTPUT_HANDLING.
- **Most confused with:** PROMPT_INJECTION_INDIRECT, and secondarily
  AGENT_PRIVILEGE_ABUSE, when the poisoned tool was used to reach something the
  agent was already entitled to reach.

## AGENT_PRIVILEGE_ABUSE

- **Definition:** an agent takes an action, or grants itself an action, outside the
  scope of the task it was given, using the authority the system handed it.
- **Inclusion test:** Does the source state that the agent used a permission, tool
  or credential to act beyond the user's stated intent, rather than merely
  following instructions faithfully?
- **Tie-break rule:** Key on persistence of the gain. If the attacker gains
  something that outlives the single request, such as new credentials, a new tool
  binding, a configuration change or an account takeover, the entry is
  AGENT_PRIVILEGE_ABUSE. If the gain is a bounded, one-off action the tool itself
  was designed to permit, the entry is classified by the mechanism that permitted
  it. If the gain is data leaving the system boundary, the entry is
  DATA_EXFILTRATION.
- **Most confused with:** DATA_EXFILTRATION, where the observable loss is the
  file rather than the enlarged authority.

## DATA_EXFILTRATION

- **Definition:** data held by the system crosses a trust boundary into attacker
  control.
- **Inclusion test:** Does the source state that records, documents, source code,
  prompts, conversation history or internal system data reached the attacker or an
  attacker-controlled destination?
- **Tie-break rule:** Key on the item set the source names. If any item in that set
  is a credential, secret, token or key, the entry is CREDENTIAL_EXPOSURE.
  Otherwise, if the gain is authority the agent acquired rather than data it read,
  the entry is AGENT_PRIVILEGE_ABUSE. Otherwise it is DATA_EXFILTRATION.
- **Most confused with:** CREDENTIAL_EXPOSURE, decided by inspecting the item set
  the source names rather than by how damaging it felt.

## SUPPLY_CHAIN_PACKAGE

- **Definition:** the compromise or the deception happens in the ecosystem of
  installable software packages. This class covers two distinct mechanisms, and an
  entry must say which one it is.
  - *Malicious package:* an attacker-authored package, or a legitimate package with
    an added malicious install script or dependency, that real users or real build
    systems resolved and installed.
  - *Hallucinated or typosquat registration:* a package name a code model invented,
    or a name that squats a well-known one, which an attacker registered in a public
    index so that plausible generated install commands resolve to it.
- **Inclusion test (malicious package):** Does a package in a public or internal
  index contain code that its author should not have shipped, and did the source
  report that it was installed or fetched by someone?
- **Inclusion test (hallucinated or typosquat registration):** Did a package name
  that was never published by the project it names get registered by an attacker,
  and did the source state that a model or a developer was misled into installing
  it?
- **Tie-break rule:** Key on whether the name resolves in an index. If the artefact
  was distributed through a package index, or is a name that resolves in one, the
  entry is SUPPLY_CHAIN_PACKAGE. If the code was produced by the model itself and
  never existed in any index, the entry is CODE_ASSISTANT_ABUSE. If the artefact
  distributed was model weights rather than a package, the entry is
  SUPPLY_CHAIN_MODEL.
- **Most confused with:** SUPPLY_CHAIN_MODEL, where the poisoned artefact is a
  checkpoint instead of a package.

## SUPPLY_CHAIN_MODEL

- **Definition:** the compromise happens to a model artefact rather than to a
  package, covering tampered or maliciously trained weights, unsafe model
  serialisation such as pickle-based formats that execute code on load, and abuse
  of a model hub as a distribution channel for unreviewed weights.
- **Inclusion test:** Was a model artefact, or a model hub account or artefact,
  the thing that carried the compromise?
- **Tie-break rule:** Key on the direction of the compromise. If the attacker
  planted or tampered with the artefact that others later loaded, the entry is
  SUPPLY_CHAIN_MODEL. If the attacker removed a model, checkpoint or training set
  from its owner, the entry is MODEL_THEFT_EXTRACTION. If the attacker only
  influenced data that had not yet been trained into any artefact, the entry is
  TRAINING_DATA_POISONING.
- **Most confused with:** SUPPLY_CHAIN_PACKAGE (package index versus model
  artefact) and MODEL_THEFT_EXTRACTION (planting versus taking).

## CODE_ASSISTANT_ABUSE

- **Definition:** harmful behaviour enters a codebase through a coding assistant's
  output, covering insecure code that is merged, plausible-but-fabricated
  dependencies, and edits an agent applied that no one reviewed line by line.
- **Inclusion test:** Was the defective code produced by a coding model, and did the
  source describe that defective code reaching a repository, a build or a running
  system?
- **Tie-break rule:** Key on whether an automated sink consumed the output. If an
  interpreter, shell, deserialiser or browser consumed the generated text without
  human or agent review, the entry is INSECURE_OUTPUT_HANDLING. If a person or an
  agent reviewed and accepted the code, or applied the edit as a diff, the entry is
  CODE_ASSISTANT_ABUSE. If the source shows no review step either way, the entry is
  CODE_ASSISTANT_ABUSE.
- **Most confused with:** INSECURE_OUTPUT_HANDLING, decided by whether review
  occurred before execution.

## TRAINING_DATA_POISONING

- **Definition:** an attacker influences the data a model is or will be trained on,
  so that the resulting behaviour carries the attacker's intent.
- **Inclusion test:** Did the source state that attacker-controlled data entered a
  training corpus, a fine-tuning set or a labelling pipeline and the resulting
  model exhibited the induced behaviour?
- **Tie-break rule:** Key on persistence of the payload. If the payload was
  written into weights and the attack still works with no attacker-controlled
  content present at inference time, the entry is TRAINING_DATA_POISONING. If the
  payload only ever needed to be present in the context at inference time, the
  entry is PROMPT_INJECTION_DIRECT or PROMPT_INJECTION_INDIRECT according to which
  channel carried it.
- **Most confused with:** PROMPT_INJECTION_INDIRECT, separated by whether the
  payload survives without attacker-controlled context.

## MODEL_THEFT_EXTRACTION

- **Definition:** a model, its weights, its architecture or its training data is
  copied out of its owner's control, including unauthorised bulk extraction and
  systematic distillation and scraping runs.
- **Inclusion test:** Did the source state that weights, checkpoints, an
  architecture or a training set left the owner's control without authorisation?
- **Tie-break rule:** Key on direction of movement. If the artefact left the
  owner's control, the entry is MODEL_THEFT_EXTRACTION. If the owner pulled a
  tampered artefact in, the entry is SUPPLY_CHAIN_MODEL. If the attacker obtained
  only generated outputs and no weights, and the source describes that as the
  target, the entry is MODEL_THEFT_EXTRACTION as well; the entry's `impact` must
  then say that only outputs were obtained.
- **Most confused with:** SUPPLY_CHAIN_MODEL, decided by direction of movement.

## JAILBREAK

- **Definition:** user-supplied text defeats the model's built-in refusal or safety
  behaviour, producing content the unmodified model would have declined to produce.
- **Inclusion test:** Did the source state that the model's own safety behaviour
  was the control that failed, and that the control was bypassed rather than
  removed by configuration?
- **Tie-break rule:** Key on the control that failed. If the model's refusal
  behaviour is the control that gave way, the entry is JAILBREAK. If the control
  that gave way is the application's handling of the model's output, the entry is
  INSECURE_OUTPUT_HANDLING. If the control that gave way is the operator's
  configuration or filter outside the model, the entry is classified by the
  mechanism the source describes, and the entry's `impact` records the bypassed
  refusal.
- **Most confused with:** PROMPT_INJECTION_DIRECT, decided by whether the aim was a
  refused output or a redirected task.

## INSECURE_OUTPUT_HANDLING

- **Definition:** the application's treatment of model output is itself the
  vulnerability, for example passing generated text to a shell, an evaluator, a
  template renderer or a deserialiser.
- **Inclusion test:** Was the defect in code written by the application around the
  model, which consumed the model's output unsafely?
- **Tie-break rule:** Key on which component the source names as defective. If the
  defective component is the application's use of the output, the entry is
  INSECURE_OUTPUT_HANDLING. If the defective component is the content of a tool
  definition the operator publishes, the entry is TOOL_POISONING. If the defective
  component is the code a coding model wrote and a reviewer accepted, the entry is
  CODE_ASSISTANT_ABUSE.
- **Most confused with:** CODE_ASSISTANT_ABUSE, decided by whether a review step sat
  between generation and execution.

## CREDENTIAL_EXPOSURE

- **Definition:** a secret intended for one principal becomes readable or usable by
  another, including keys, tokens, passwords, connection strings and personal
  credentials held in prompts, logs, repositories or model context.
- **Inclusion test:** Does the source name a credential as the item that was
  exposed, leaked or usable by an unintended party?
- **Tie-break rule:** Key on the item. If the exposed item is a credential, the
  entry is CREDENTIAL_EXPOSURE regardless of which mechanism exposed it. If the
  exposed items are records or documents, the entry is DATA_EXFILTRATION. If no
  credential and no data record is named, the entry is classified by the mechanism.
- **Most confused with:** DATA_EXFILTRATION, decided by the item set the source
  names.

## DENIAL_OF_SERVICE

- **Definition:** attacker-controlled input degrades or removes availability,
  through resource exhaustion, quota consumption, queue flooding or sustained
  inference cost.
- **Inclusion test:** Was the outcome unavailability or unacceptable cost, with no
  attacker capability gained beyond having consumed the resource?
- **Tie-break rule:** Key on what the attacker obtained. If the source describes
  any capability, credential or data the attacker gained, the entry is classified by
  the step that yielded it. DENIAL_OF_SERVICE applies only when the source
  describes no gain beyond consumption. If the exhaustion was achieved through a
  specific published weakness with its own remedy, the entry still takes this class
  and names the weakness in `mitigation`.
- **Most confused with:** JAILBREAK or PROMPT_INJECTION_DIRECT, when the attack
  began as a crafted input but the only stated outcome was cost or unavailability.

## OTHER

- **Definition:** the escape hatch for a real, documented attack on an AI system
  that none of the fourteen named classes describes.
- **Inclusion test:** Does the entry's `impact` field state why no named class
  fits, naming the mechanism and the property that no class tests for? An entry
  with no such justification is not ready to file.
- **Tie-break rule:** Key on whether the mechanism can be expressed as a class
  test. If the attack differs from a named class only in scale or target, it is
  that named class. If the attack uses a genuinely different mechanism, it is OTHER,
  and `impact` must say so. OTHER is never a label for a tie-break the curator did
  not want to make.
- **Most confused with:** CODE_ASSISTANT_ABUSE, which absorbs most novel-sounding
  developer-tool incidents.

### On the use of OTHER

OTHER is the class most likely to be misused, and overuse of it is a curator smell
that must be reviewed rather than shipped. A batch where OTHER is common usually
means either that a genuinely new mechanism has appeared and deserves a class in a
later schema version, or that the curator stopped applying the inclusion tests. Both
are findings worth publishing, and both belong in the `impact` text of the entries
involved.
