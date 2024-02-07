FROM condaforge/mambaforge as base


# Directory Creation
ENV APP_ROOT /opt/app
RUN mkdir $APP_ROOT && \
    mkdir /etc/app
WORKDIR $APP_ROOT


FROM base as requirements
COPY ./environment.yml $APP_ROOT/

RUN mamba env create --quiet --force environment.yml
RUN mamba clean --quiet --all --yes
SHELL ["mamba", "run", "-n", "chatup-chat", "/bin/bash", "-c"]

FROM requirements as container
COPY . .
RUN chmod +x entrypoint.sh

EXPOSE $APP_EXPOSED_PORT
ENV FLASK_DEBUG 1
CMD ["./entrypoint.sh"]
