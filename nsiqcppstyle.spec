Name:           python-nsiqcppstyle
Version:        0.5.1
Release:        1%{?dist}
Summary:        C++ style checker

License:        GPL-2
URL:            https://github.com/kunaltyagi/nsiqcppstyle
#Source:         #{url}/archive/v#{version}/nsiqcppstyle-#{version}.tar.gz
Source:         nsiqcppstyle-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-tomli
BuildRequires:  python3-hatchling
BuildRequires:  python3-tox-current-env
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
nsiqcppstyle is one of the most customizable cpp style
checkers about.}

%description %_description

%package -n python3-nsiqcppstyle
Summary:        %{summary}

%description -n python3-nsiqcppstyle %_description

%prep
%autosetup -p1 -n nsiqcppstyle-%{version}


#generate_buildrequires
#pyproject_buildrequires -t


%build
#py3_build                                                                                                                                 
%{?el7:python3.8 -m build}
%{?el8:%pyproject_wheel}
%{?el9:%pyproject_wheel}
%{?fedora:%pyproject_wheel}


%install
#py3_install                                                                                                                               
%{?el7:python3.8 -m build}
%{?el8:%pyproject_install}
%{?el9:%pyproject_install}
%{?fedora:%pyproject_install}

# Here, "nsiqcppstyle" is the name of the importable module.
%pyproject_save_files -l nsiqcppstyle


#check
#tox


# Note that there is no %%files section for
# the unversioned python module, python-nsiqcppstyle.

# For python3-nsiqcppstyle, %%{pyproject_files} handles code files and %%license,
# but executables and documentation must be listed in the spec file:

%files -n python3-nsiqcppstyle -f %{pyproject_files}
%doc README.md
%{_bindir}/*

%changelog
