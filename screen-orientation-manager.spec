Name:           screen-orientation-manager
Version:        1.4
Release:        1%{?dist}
Summary:        Screen Orientation Manager for X11

License:        GPL-3.0
URL:            https://github.com/archisman-panigrahi/surface-RT-screen-rotator
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  meson
BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils
Requires:       python3
Requires:       python3-gobject
Requires:       gtk3
Recommends:     ayatana-indicator-application

%description
This app rotates the touchscreen, display and touchpad orientation of convertible laptops and tablets running X11 based desktop environments.

%prep
%autosetup

%build
meson setup builddir
meson compile -C builddir

%install
meson install -C builddir --destdir=%{buildroot}

%files
%license LICENSE
%doc README.md
/usr/bin/screen-orientation-manager
%{_datadir}/screen-orientation-manager/
%{_datadir}/applications/screen-orientation-manager.desktop
%{_datadir}/icons/hicolor/scalable/apps/screen-orientation-manager.svg

%changelog
* Sat Aug 17 2025 Archisman Panigrahi <apandada1@gmail.com> - 1.4-1
- Initial RPM release
