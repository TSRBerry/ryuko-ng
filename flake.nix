{
  description = "Application packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }@inputs:

    let
      ryuko_overlay = final: prev:
        let
          pkgs = import nixpkgs { system = prev.system; };
          poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
        in {
          ryuko-ng = with final;
            poetry2nix.mkPoetryApplication rec {
              projectDir = self;
              src = projectDir;
              overrides = [ poetry2nix.defaultPoetryOverrides (self: super: {
                cryptography = super.cryptography.overridePythonAttrs (old: {
                  cargoDeps = pkgs.rustPlatform.fetchCargoTarball {
                    src = old.src;
                    sourceRoot = "${old.pname}-${old.version}/src/rust";
                    name = "${old.pname}-${old.version}";
                    # cryptography-42.0.5
                    sha256 = "sha256-Pw3ftpcDMfZr/w6US5fnnyPVsFSB9+BuIKazDocYjTU=";
                  };
                });
              }) ];
            };
        };
    in flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlays."${system}" ];
        };
      in {
        packages = {
          default = self.packages.${system}.ryuko-ng;
          ryuko-ng = pkgs.ryuko-ng;
        };

        overlays = ryuko_overlay;

        nixosModules.ryuko-ng = { pkgs, lib, config, ... }: {
          options = let inherit (lib) mkEnableOption mkOption types;
          in {
            services.ryuko-ng = {
              enable = mkEnableOption (lib.mdDoc "ryuko-ng discord bot");
            };
          };

          config = let
            inherit (lib) mkIf;
            cfg = config.services.ryuko-ng;
          in mkIf cfg.enable {
            nixpkgs.overlays = [ self.overlays."${system}" ];

            systemd.services.ryuko-ng = {
              description = "ryuko-ng bot";
              after = [ "network.target" ];
              wantedBy = [ "multi-user.target" ];
              script = ''
                ${pkgs.ryuko-ng.dependencyEnv}/bin/python3 -m robocop_ng /var/lib/ryuko-ng
              '';

              serviceConfig = rec {
                Type = "simple";
                User = "ryuko-ng";
                Group = "ryuko-ng";
                StateDirectory = "ryuko-ng";
                StateDirectoryMode = "0700";
                CacheDirectory = "ryuko-ng";
                CacheDirectoryMode = "0700";
                UMask = "0077";
                WorkingDirectory = "/var/lib/ryuko-ng";
                Restart = "on-failure";
              };
            };

            users = {
              users.ryuko-ng = {
                group = "ryuko-ng";
                isSystemUser = true;
              };
              extraUsers.ryuko-ng.uid = 989;

              groups.ryuko-ng = { };
              extraGroups.ryuko-ng = {
                name = "ryuko-ng";
                gid = 987;
              };
            };
          };
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.ryuko-ng ];
          packages = [ pkgs.poetry ];
        };

        checks = {
          vmTest = with import (nixpkgs + "/nixos/lib/testing-python.nix") {
            inherit system;
          };
            makeTest {
              name = "ryuko-ng nixos module testing ${system}";

              nodes = {
                client = { ... }: {
                  imports = [ self.nixosModules.${system}.ryuko-ng ];

                  services.ryuko-ng.enable = true;
                };
              };

              testScript = ''
                client.wait_for_unit("ryuko-ng.service")
              '';
            };

        };

        formatter = pkgs.nixfmt;
      });
}
