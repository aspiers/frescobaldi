\version "2.13.43"
\include "bar_defaults.ily"
\layout {
  \context {
    \Score
    \override BarLine #'extra-offset = #'(-1.5 . 0)
  }
}
{ s \bar ":|.|:" s }