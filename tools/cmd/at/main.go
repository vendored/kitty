package main

import (
	"fmt"
	"os"

	"github.com/fatih/color"
	"github.com/spf13/cobra"

	"kitty/tools/cli"
	"kitty/tools/crypto"
)

var encrypt_cmd = crypto.Encrypt_cmd
var exe_name = "kitty-at"

func main() {
	var root = cli.CreateCommand(&cobra.Command{
		Use:   "[global options] command [command options] [command args]",
		Short: "Control kitty remotely",
		Long:  "Control kitty by sending it commands. Set the allow_remote_control option in kitty.conf or use a password, for this to work.",
		Run: func(cmd *cobra.Command, args []string) {
            cmd.Usage()
            fmt.Fprintln(os.Stderr, color.RedString("\nNo command specified for " + exe_name))
		},
	}, exe_name)
	cli.PersistentChoices(root, "use-password", "If no password is available, kitty will usually just send the remote control command without a password. This option can be used to force it to always or never use the supplied password.", "if-available", "always", "never")
	root.Annotations["options_title"] = "Global options"
	cli.Init(root)
	if err := root.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
