function walker(nothing)
%comments here 
%1D Langevin equation 
%integrates using Bussi integrator:
%Bussi and Parrinello, PRE, 2007, 056707

%define parameters

steps=1000000;
iratio=1000;
mratio=1000;
movieflag = 10; % set to 1 to make movie
x0 = 2.0;
T = 310; %initial temperature
dt = .005; %time step
t=0; %time
m=1; %mass
fprintf('%s\n','Parameters:');
fprintf(' Number of steps %5i \n',steps);
fprintf(' Initial x coord %2.2f \n',x0);
fprintf(' "Temperature" %3.2f \n',T);
fprintf(' Timestep %2.2e \n',dt);

%parameters for integrator
gamma=5.0;
beta=1/T/1.987e-3; %assum V is in kcal/mol
c1=exp(-gamma*dt/2);
c2=sqrt( (1-c1^2)*m/beta);

fprintf('\n  c1: %5.5f \n', c1);
fprintf('  c2: %5.5f \n', c2);

%metadynamics parameters
w=.4;
delta=0.1;
hfreq=3000;

%plot 1D fes
xlong=(-4:.01:4);
[vcalc,first]=force(xlong,0,w,delta);
plot(xlong,vcalc,'',xlong,first,'LineWidth',2)
set(gca,'FontSize',14)
xlabel('CV (s)','FontSize',16);ylabel('F(s) (arb)','FontSize',16);

%initial configuration
q=zeros(1,steps);
E=zeros(1,steps);
q(1)=x0;
v0=rand(1)-0.5;
p=v0*m;
s(1)=0;
[v,f]=force(q(1),0,w,delta);
E(1)=0.5*p^2+v;


plot(xlong,vcalc,'',x0,v,'ro','MarkerSize',10, ...
   'markerfacecolor','r');xlabel('s');ylabel('F (arb)');
   xlim([-4 4]);ylim([-12 6]);
%loop over number of steps


if (movieflag==1)
  mkdir movie;
  delete movie   
  rmdir movie;
  mkdir movie;
  frame = 0;
end

for i=1:steps
  first check if we should deposit
  a hill on the FES
  if(mod(i,hfreq)==0)
    len=length(s);
    if(i==hfreq)
      s(1) = q(i);
    else
      s(len+1) = q(i);
    end
  end
  [v,f]=force(q(i),s,w,delta);
  q(i)
  R1=rand(1)-0.5;
  R2=rand(1)-0.5;
  
  pplus=c1*p + c2*R1;
  q(i+1)=q(i)+(pplus/m)*dt + f/m*(dt^2/2);
  [v2,f2] = force(q(i+1),s,w,delta);
  pminus=pplus+(f/2 + f2/2)*dt;
  p=c1*pminus+c2*R2;

  E(i+1)=0.5*p^2+v2;
 if(mod(i,iratio)==0)
    %fprintf ('\n%5i %3.3f %3.3f %3.3f',i,q(i),f,E(i+1));
    
    %sum Gaussians
    bias=vcalc;
    if (length(s)>1)
     for(k=1:length(xlong))
      bias(k)=bias(k)+sum(w.*exp(-(xlong(k)-s).^2 ...
                   ./2./delta.^2));
     end
    end
    
    v=v+sum(w.*exp(-(q(i+1)-s).^2./2./delta^2));
  %  plot(xlong,bias,'LineWidth',4,xlong,vcalc,q(i+1),v,'ro','MarkerSize',10, ...
  % 'markerfacecolor','r');set(gca,'FontSize',14);xlabel('CV (s)','FontSize',16);
  
    % plot(xlong,bias,xlong,vcalc,q(i+1),v,'ro', ...
    %  'MarkerSize',10,'markerfacecolor','r');
      plot(xlong,bias,'LineWidth',2,'color','red');
      hold on;
      plot(xlong,vcalc,'LineWidth',2);
      plot(q(i+1),v,'ro','MarkerSize',10,'markerfacecolor','r', ...
          'LineWidth',3);
      set(gca,'FontSize',14);xlabel('CV (s)','FontSize',16);
      hold off;
 %  plot(xlong,vcalc,'',x0,v,'ro','MarkerSize',10, ...
 %  'markerfacecolor','r');xlabel('s');ylabel('F (arb)');
    ylabel('F(s) (arb)','FontSize',16);
      xlim([-4 4]);ylim([-12 6]);

    pause(.0001) %required to update plot
      
     if(mod(i,iratio)==0)   
       if (movieflag==1)
          set(gcf, 'renderer', 'painters');
          set(gcf, 'PaperUnits', 'inches');
          set(gcf, 'PaperSize', [30.0 30.0]);
          set(gcf,'PaperPosition',[0 0 6 9]);
          [x,map]=getframe(gcf);
          filename=strcat('movie/file_',num2str(frame),'.png');
          %imwrite(x,filename,'png');
          print(gcf, '-dpng', filename);
          frame = frame+1;
       end
     end
 end
end  %end loop over steps



return
%end of main function

%begin subfunctions

%calculate PE and force 
function [V,F]=force(r,s,w,delta)

V=-5*exp(-(r-2/0.75).^2) - 10*exp(-(r + 2/0.75).^2);
Fpot=-5.*2.*-(r-2/0.75).*exp(-(r-2/0.75).^2)...
    -10.*2.*-(r+2/0.75).*exp(-(r + 2/0.75).^2);

Fbias=sum(w.*(r-s)./delta^2.*exp(-(r-s).^2./2./delta.^2));

F=Fpot*-1+Fbias;
 if (r<-4) 
   V=100*(r+4)^4;
   F=-100*4*(r+4);
 elseif (r>4)
   V=100*(r-4)^4;
   F=-100*4*(r-4);
 end
 
 