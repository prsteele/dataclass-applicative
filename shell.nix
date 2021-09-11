{ sources ? import ./nix/sources.nix
, pkgs ? import sources.nixpkgs { }
}:
let
  app = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    editablePackageSources = {
      dataclass-applicative = ./dataclass_applicative;
    };
    python = pkgs.python39Full;
  };
in
pkgs.mkShell {
  buildInputs = [ app pkgs.black pkgs.python-language-server ];
}
