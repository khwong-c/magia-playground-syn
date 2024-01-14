# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.11 as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip install \
    --target ${FUNCTION_DIR} \
        awslambdaric


FROM python:3.11-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Install Yosys
RUN apt-get update -y && apt-get install -y \
    yosys \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Lambda Function
COPY lambda_function.py ${FUNCTION_DIR}

ENV LAMBDA_TASK_ROOT=${FUNCTION_DIR}
ENV LAMBDA_RUNTIME_DIR=/var/runtime

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "lambda_function.handler" ]

# COPY ./entry_script.sh /entry_script.sh
# RUN chmod +x /entry_script.sh
# ADD aws-lambda-rie /usr/local/bin/aws-lambda-rie
# ENTRYPOINT [ "/entry_script.sh","lambda_function.handler" ]
