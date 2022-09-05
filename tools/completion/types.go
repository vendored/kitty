// License: GPLv3 Copyright: 2022, Kovid Goyal, <kovid at kovidgoyal.net>

package completion

type Match struct {
	word        string
	description string
}

type MatchGroup struct {
	Title                    string
	NoTrailingSpace, IsFiles bool
	Matches                  []Match
}

type Completions struct {
	Groups MatchGroup

	current_cmd *command
}

type completion_func func(completions *Completions, partial_word string)

type option struct {
	name               string
	aliases            []string
	description        string
	has_following_arg  bool
	completion_for_arg completion_func
}

type command struct {
	options                []option
	subcommands            []command
	subcommands_title      string
	completion_for_arg     completion_func
	stop_processing_at_arg int
}
