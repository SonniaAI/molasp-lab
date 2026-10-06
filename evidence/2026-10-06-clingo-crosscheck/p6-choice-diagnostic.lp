% p6-choice-diagnostic.lp — enumeration-completeness diagnostic (not one of the five)
% two stable models {a} and {b}; full enumeration must return BOTH
a :- not b.
b :- not a.
