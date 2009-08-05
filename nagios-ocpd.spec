%include	/usr/lib/rpm/macros.perl
Summary:	Obsessive Compulsive Host/Service Processor Daemon for Nagios
Name:		nagios-ocpd
Version:	1.0
Release:	0.13
License:	GPL v2+
Group:		Networking/Daemons
Source0:	ocpd.pl
Source1:	README
Source2:	ocpd.init
URL:		http://wiki.nagios.org/index.php/OCP_Daemon
BuildRequires:	perl-Event-Lib
BuildRequires:	perl-base
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	nagios >= 3.1.2-6
Requires:	nagios-nsca-client
Requires:	perl-Event-Lib >= 1.03-1
Requires:	rc-scripts
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libdir		%{_prefix}/lib/nagios
%define		_spooldir	%{_var}/spool/nagios

%description
Given the way Nagios operates, running a command every time a
host/service check result comes in can greatly reduce the speed at
which Nagios can do its work. On huge Nagios setups the checks can end
up lagging behind without fully using the server resources.

There is a way to make Nagios write OCHP/OCSP data into a named pipe
instead of running a command every time, and on the other end of the
pipe a daemon takes care of sending the data to the master Nagios
server.

%prep
%setup -qcT
install %{SOURCE0} .
cp %{SOURCE1} .

%build
%{__perl} -c ocpd.pl

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir},%{_spooldir},/etc/rc.d/init.d}
install ocpd.pl $RPM_BUILD_ROOT%{_libdir}/ocpd
touch $RPM_BUILD_ROOT%{_spooldir}/host-perfdata.fifo
touch $RPM_BUILD_ROOT%{_spooldir}/service-perfdata.fifo
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
for f in service-perfdata.fifo host-perfdata.fifo; do
	if [ ! -e %{_spooldir}/$f ]; then
		mkfifo -m 600 %{_spooldir}/$f
		chown nagios:nagios %{_spooldir}/$f
	fi
done

/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc README
%attr(754,root,root) /etc/rc.d/init.d/nagios-ocpd
%attr(755,root,root) %{_libdir}/ocpd
%attr(600,nagios,nagios) %ghost %{_spooldir}/host-perfdata.fifo
%attr(600,nagios,nagios) %ghost %{_spooldir}/service-perfdata.fifo
